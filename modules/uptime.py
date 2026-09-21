"""Uptime watcher for Franklin's GitHub Pages sites.

Only sends a message when a site's status *changes* (up→down or down→up) —
no repeated daily alerts while a site stays down, and no noise when
everything is fine.
"""
import requests
from html import escape

SITES = {
    "Portfolio": "https://damien222201.github.io/my-portfolio/",
    "HeXeNe Website": "https://damien222201.github.io/HeXeNe-Website/",
}


def _check(url):
    try:
        resp = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        return "up" if resp.status_code < 400 else "down"
    except Exception:
        return "down"


def get_section(state):
    uptime_state = state["uptime"]
    changes = []

    for name, url in SITES.items():
        current = _check(url)
        previous = uptime_state.get(url)
        if previous is not None and previous != current:
            changes.append((name, url, previous, current))
        uptime_state[url] = current

    state["uptime"] = uptime_state

    if not changes:
        return None  # nothing changed — don't send a message

    lines = ["<b>🚦 Site Status Change</b>", ""]
    for name, url, previous, current in changes:
        icon = "✅" if current == "up" else "🔴"
        lines.append(f"{icon} <b>{escape(name)}</b>: {previous} → {current}\n{escape(url)}")
    return "\n".join(lines)
