"""xAI OAuth authorization_code + PKCE (mirror 9router / CLIProxyAPI).

9router source: app/src/lib/oauth/services/xai.js
  - response_type=code, redirect http://127.0.0.1:56121/callback
  - PKCE S256, 96-byte verifier
  - plan=generic, referrer=cli-proxy-api
  - exchange: grant_type=authorization_code (public client, no secret)

Device-code grant is a different path and often gets invalid_grant Access denied
after UI "Device Authorized". This module is the grant that manual 9router uses.
"""

from __future__ import annotations

import base64
import hashlib
import json
import secrets
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Callable
from urllib.parse import parse_qs, urlparse

from .proxyutil import resolve_proxy
import requests

# Same Grok CLI / CPA client as device flow + 9router grok-cli
CLIENT_ID = "b1a00492-073a-47ea-816f-4c329264a828"
ISSUER = "https://auth.x.ai"
AUTHORIZE_URL = f"{ISSUER}/oauth2/authorize"
TOKEN_URL = f"{ISSUER}/oauth2/token"
SCOPE = "openid profile email offline_access grok-cli:access api:access"
LOOPBACK_HOST = "127.0.0.1"
LOOPBACK_PORT = 56121
CALLBACK_PATH = "/callback"
DEFAULT_REDIRECT_URI = f"http://{LOOPBACK_HOST}:{LOOPBACK_PORT}{CALLBACK_PATH}"
PKCE_VERIFIER_BYTES = 96
USER_AGENT = "grok-cli/9router"

LogFn = Callable[[str], None]


def _noop_log(_: str) -> None:
    return None


def _b64url(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def generate_code_verifier(n_bytes: int = PKCE_VERIFIER_BYTES) -> str:
    return _b64url(secrets.token_bytes(n_bytes))


def generate_code_challenge(verifier: str) -> str:
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    return _b64url(digest)


def generate_state() -> str:
    return _b64url(secrets.token_bytes(32))


def generate_nonce() -> str:
    return secrets.token_bytes(16).hex()


@dataclass
class AuthCodeSession:
    code_verifier: str
    code_challenge: str
    state: str
    nonce: str
    redirect_uri: str
    authorize_url: str


@dataclass
class TokenResult:
    access_token: str
    refresh_token: str
    id_token: str | None
    token_type: str
    expires_in: int
    raw: dict[str, Any]


class OAuthAuthCodeError(RuntimeError):
    pass


def build_authorize_url(
    *,
    redirect_uri: str = DEFAULT_REDIRECT_URI,
    client_id: str = CLIENT_ID,
    scope: str = SCOPE,
    code_challenge: str,
    state: str,
    nonce: str | None = None,
    authorize_url: str = AUTHORIZE_URL,
) -> str:
    """Build auth URL matching 9router XaiService.buildXaiAuthUrl."""
    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": scope,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "state": state,
        "nonce": nonce or generate_nonce(),
        "plan": "generic",
        "referrer": "cli-proxy-api",
    }
    # encodeURIComponent style: spaces as %20 not +
    qs = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    return f"{authorize_url}?{qs}"


def create_auth_session(
    *,
    redirect_uri: str = DEFAULT_REDIRECT_URI,
    client_id: str = CLIENT_ID,
) -> AuthCodeSession:
    verifier = generate_code_verifier()
    challenge = generate_code_challenge(verifier)
    state = generate_state()
    nonce = generate_nonce()
    url = build_authorize_url(
        redirect_uri=redirect_uri,
        client_id=client_id,
        code_challenge=challenge,
        state=state,
        nonce=nonce,
    )
    return AuthCodeSession(
        code_verifier=verifier,
        code_challenge=challenge,
        state=state,
        nonce=nonce,
        redirect_uri=redirect_uri,
        authorize_url=url,
    )


class _CallbackHTTPServer(HTTPServer):
    """HTTPServer with capture slots used by _CallbackHandler."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.capture_lock = threading.Lock()
        self.capture_event = threading.Event()
        self.capture_params: dict[str, str] = {}


class _CallbackHandler(BaseHTTPRequestHandler):
    """Minimal loopback; server instance holds capture state."""

    def log_message(self, fmt: str, *args: Any) -> None:  # noqa: A003
        return

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path_ok = parsed.path.rstrip("/") == CALLBACK_PATH.rstrip("/") or parsed.path == CALLBACK_PATH
        if not path_ok:
            self.send_response(404)
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(b"not found")
            return
        qs = parse_qs(parsed.query)
        server: _CallbackHTTPServer = self.server  # type: ignore[assignment]
        with server.capture_lock:
            server.capture_params = {k: (v[0] if v else "") for k, v in qs.items()}
            server.capture_event.set()
        body = (
            b"<html><body><h3>xAI OAuth OK</h3>"
            b"<p>You can close this tab.</p></body></html>"
        )
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Connection", "close")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class LoopbackServer:
    """Bind 127.0.0.1:56121/callback and wait for ?code= (9router port)."""

    def __init__(self, port: int = LOOPBACK_PORT, host: str = LOOPBACK_HOST) -> None:
        self.host = host
        self.port = port
        self._httpd: _CallbackHTTPServer | None = None
        self._thread: threading.Thread | None = None

    @property
    def redirect_uri(self) -> str:
        return f"http://{self.host}:{self.port}{CALLBACK_PATH}"

    def start(self) -> None:
        try:
            self._httpd = _CallbackHTTPServer((self.host, self.port), _CallbackHandler)
        except OSError as e:
            raise OAuthAuthCodeError(
                f"cannot bind {self.host}:{self.port} (stop 9router OAuth or free port): {e}"
            ) from e
        self._thread = threading.Thread(target=self._httpd.serve_forever, daemon=True)
        self._thread.start()

    def snapshot(self) -> dict[str, str] | None:
        if self._httpd is None or not self._httpd.capture_event.is_set():
            return None
        with self._httpd.capture_lock:
            return dict(self._httpd.capture_params)

    def wait(self, timeout: float = 240.0) -> dict[str, str]:
        if self._httpd is None:
            raise OAuthAuthCodeError("loopback not started")
        if not self._httpd.capture_event.wait(timeout):
            raise OAuthAuthCodeError("auth-code callback timed out (no redirect to loopback)")
        with self._httpd.capture_lock:
            return dict(self._httpd.capture_params)

    def close(self) -> None:
        if self._httpd is not None:
            httpd = self._httpd
            def _bg_close():
                try:
                    httpd.shutdown()
                except Exception:
                    pass
                try:
                    httpd.server_close()
                except Exception:
                    pass
            threading.Thread(target=_bg_close, daemon=True).start()
            self._httpd = None


def _opener(proxy: str | None = None) -> urllib.request.OpenerDirector:
    p = resolve_proxy(proxy)
    if not p:
        return urllib.request.build_opener()
    ph = urllib.request.ProxyHandler({"http": p, "https": p})
    return urllib.request.build_opener(ph)


def exchange_code(
    *,
    code: str,
    code_verifier: str,
    redirect_uri: str = DEFAULT_REDIRECT_URI,
    client_id: str = CLIENT_ID,
    token_url: str = TOKEN_URL,
    timeout: float = 30.0,
    proxy: str | None = None,
    log: LogFn | None = None,
) -> TokenResult:
    log = log or _noop_log
    form = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "code": code,
        "redirect_uri": redirect_uri,
        "code_verifier": code_verifier,
    }
    
    proxies = {}
    p = resolve_proxy(proxy)
    if p:
        proxies = {"http": p, "https": p}

    log(f"POST {token_url} (timeout={timeout}, proxies={proxies})")
    try:
        resp = requests.post(
            token_url,
            data=form,
            headers={
                "Accept": "application/json",
                "User-Agent": USER_AGENT,
            },
            proxies=proxies,
            timeout=timeout,
        )
        status = resp.status_code
        body = resp.text
        log(f"POST response status={status} body_len={len(body)}")
        try:
            parsed = resp.json()
        except Exception:
            parsed = body
    except Exception as e:
        log(f"POST error: {e}")
        raise OAuthAuthCodeError(f"token exchange failed: {e}") from e

    if status != 200 or not isinstance(parsed, dict) or not parsed.get("access_token"):
        raise OAuthAuthCodeError(f"token exchange failed HTTP {status}: {parsed!r}")

    refresh = str(parsed.get("refresh_token") or "").strip()
    if not refresh:
        raise OAuthAuthCodeError("token response missing refresh_token")
    return TokenResult(
        access_token=str(parsed["access_token"]).strip(),
        refresh_token=refresh,
        id_token=(str(parsed["id_token"]).strip() if parsed.get("id_token") else None),
        token_type=str(parsed.get("token_type") or "Bearer"),
        expires_in=int(parsed.get("expires_in") or 21600),
        raw=parsed,
    )


def parse_callback_url(url: str) -> dict[str, str]:
    """Extract query params from a full callback URL (browser landed on loopback)."""
    parsed = urlparse(url or "")
    qs = parse_qs(parsed.query)
    return {k: (v[0] if v else "") for k, v in qs.items()}


if __name__ == "__main__":
    # ponytail: PKCE shape self-check (no network)
    v = generate_code_verifier()
    c = generate_code_challenge(v)
    assert len(v) > 40 and len(c) == 43, (len(v), len(c))
    s = create_auth_session()
    assert "response_type=code" in s.authorize_url
    assert "code_challenge_method=S256" in s.authorize_url
    assert "referrer=cli-proxy-api" in s.authorize_url
    assert "plan=generic" in s.authorize_url
    assert s.redirect_uri == DEFAULT_REDIRECT_URI
    print("ok", s.authorize_url[:80])
