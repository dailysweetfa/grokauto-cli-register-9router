"""Human-like pauses for v2 register/mint.

Policy: slow + natural > fast. Success over throughput.
"""

from __future__ import annotations

import random
import time
from typing import Callable

# Defaults used when config not loaded yet
DEFAULTS = {
    "human_delay": True,
    "delay_action_sec": [0.8, 2.5],
    "delay_page_sec": [1.5, 4.0],
    "delay_between_accounts_sec": [45, 120],
    "delay_think_sec": [1.2, 3.5],
}


def _pair(cfg: dict, key: str) -> tuple[float, float]:
    raw = cfg.get(key, DEFAULTS.get(key, [0.5, 1.5]))
    if isinstance(raw, (list, tuple)) and len(raw) >= 2:
        lo, hi = float(raw[0]), float(raw[1])
    else:
        lo = hi = float(raw or 1)
    if hi < lo:
        lo, hi = hi, lo
    return max(0.0, lo), max(0.0, hi)


def enabled(cfg: dict | None = None) -> bool:
    c = cfg if isinstance(cfg, dict) else {}
    return bool(c.get("human_delay", DEFAULTS["human_delay"]))


def seconds(kind: str = "action", cfg: dict | None = None) -> float:
    """Random seconds for a pause kind: action | page | account | think | short."""
    c = cfg if isinstance(cfg, dict) else {}
    if not enabled(c):
        return 0.15 if kind != "account" else 1.0
    key = {
        "action": "delay_action_sec",
        "page": "delay_page_sec",
        "account": "delay_between_accounts_sec",
        "think": "delay_think_sec",
        "short": "delay_action_sec",
    }.get(kind, "delay_action_sec")
    lo, hi = _pair(c, key)
    if kind == "short":
        lo, hi = lo * 0.35, hi * 0.45
    # light jitter so intervals aren't flat
    base = random.uniform(lo, hi)
    return max(0.0, base * random.uniform(0.9, 1.12))


def pause(
    kind: str = "action",
    *,
    cfg: dict | None = None,
    cancel: Callable[[], bool] | None = None,
    log: Callable[[str], None] | None = None,
    label: str = "",
) -> None:
    """Sleep human-like; cancel-aware (0.2s ticks)."""
    sec = seconds(kind, cfg)
    if sec <= 0:
        return
    if log and kind in ("account", "page", "think"):
        tag = label or kind
        log(f"[human] pause {tag}: {sec:.1f}s")
    deadline = time.time() + sec
    while True:
        if cancel and cancel():
            return
        left = deadline - time.time()
        if left <= 0:
            return
        time.sleep(min(0.2, left))


def spice(base: float, cfg: dict | None = None, factor: float = 0.35) -> float:
    """Add ±factor jitter to an existing fixed sleep (mint UI steps)."""
    c = cfg if isinstance(cfg, dict) else {}
    if not enabled(c) or base <= 0:
        return max(0.0, base)
    lo = base * (1.0 - factor)
    hi = base * (1.0 + factor)
    return max(0.05, random.uniform(lo, hi))
