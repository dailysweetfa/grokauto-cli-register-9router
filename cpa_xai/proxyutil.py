"""Resolve outbound proxy for CPA mint HTTP + browser.

Priority (highest first):
  1. explicit argument
  2. thread-local runtime pin (set_runtime_proxy)
  3. environment https_proxy / HTTPS_PROXY / http_proxy / HTTP_PROXY

Thread-local pin avoids cross-talk when multiple mint workers run with
different proxies in the same process.
"""

from __future__ import annotations

import os
import threading
from urllib.parse import urlparse

_thread = threading.local()


def set_runtime_proxy(proxy: str | None) -> None:
    """Pin proxy for the *current thread*. Empty clears pin."""
    p = (proxy or "").strip()
    _thread.proxy = p or None


def get_runtime_proxy() -> str | None:
    return getattr(_thread, "proxy", None)


def resolve_proxy(explicit: str | None = None) -> str:
    for cand in (
        (explicit or "").strip(),
        (get_runtime_proxy() or "").strip(),
        (os.environ.get("https_proxy") or "").strip(),
        (os.environ.get("HTTPS_PROXY") or "").strip(),
        (os.environ.get("http_proxy") or "").strip(),
        (os.environ.get("HTTP_PROXY") or "").strip(),
    ):
        if cand:
            return cand
    return ""


def proxy_for_chromium(proxy: str) -> str:
    """Chromium --proxy-server cannot embed user:pass; host:port only."""
    p = (proxy or "").strip()
    if not p:
        return ""
    u = urlparse(p if "://" in p else f"http://{p}")
    host = u.hostname or ""
    if not host:
        return ""
    port = u.port or (443 if (u.scheme or "http") == "https" else 80)
    scheme = u.scheme or "http"
    return f"{scheme}://{host}:{port}"


def proxy_log_label(proxy: str) -> str:
    """Redact userinfo for logs."""
    p = (proxy or "").strip()
    if not p:
        return ""
    try:
        u = urlparse(p if "://" in p else f"http://{p}")
        host = u.hostname or "?"
        port = u.port or ""
        auth = "user:***@" if u.username else ""
        return f"{u.scheme or 'http'}://{auth}{host}{(':' + str(port)) if port else ''}"
    except Exception:
        return "(proxy)"


def prepare_chrome_proxy(proxy_str: str, options: Any) -> bool:
    """If proxy has user:pass, create a temporary extension and load it.
    Returns True if extension was created and loaded, False otherwise.
    """
    import urllib.parse
    import os
    import tempfile
    import json
    
    proxy_str = (proxy_str or "").strip()
    if not proxy_str:
        return False
        
    try:
        parsed = urllib.parse.urlparse(proxy_str if "://" in proxy_str else f"http://{proxy_str}")
        if not parsed.username or not parsed.password:
            return False
            
        # Has authentication - Create temporary Chrome extension
        ext_dir = os.path.join(tempfile.gettempdir(), f"grok_proxy_auth_{parsed.port or 8080}")
        os.makedirs(ext_dir, exist_ok=True)
        
        manifest_path = os.path.join(ext_dir, "manifest.json")
        bg_path = os.path.join(ext_dir, "background.js")
        
        manifest_js = {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": "Grok Proxy Auth",
            "permissions": [
                "proxy",
                "tabs",
                "unlimitedStorage",
                "storage",
                "<all_urls>",
                "webRequest",
                "webRequestBlocking"
            ],
            "background": {
                "scripts": ["background.js"]
            },
            "minimum_chrome_version": "22.0.0"
        }
        
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest_js, f)
            
        scheme = parsed.scheme or "http"
        host = parsed.hostname or ""
        port = parsed.port or 80
        username = parsed.username or ""
        password = parsed.password or ""
        
        bg_js = f"""
var config = {{
    mode: "fixed_servers",
    rules: {{
      singleProxy: {{
        scheme: "{scheme}",
        host: "{host}",
        port: parseInt("{port}")
      }},
      bypassList: []
    }}
  }};

chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});

chrome.webRequest.onAuthRequired.addListener(
    function callback(details) {{
        return {{
            authCredentials: {{
                username: "{username}",
                password: "{password}"
            }}
        }};
    }},
    {{urls: ["<all_urls>"]}},
    ["blocking"]
);
"""
        with open(bg_path, "w", encoding="utf-8") as f:
            f.write(bg_js)
            
        options.add_extension(ext_dir)
        return True
    except Exception:
        return False

