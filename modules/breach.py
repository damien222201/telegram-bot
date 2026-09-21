"""Data breach monitor for one or more personal email addresses.

Uses XposedOrNot's free, keyless API. Only reports breaches not already
seen for a given email (tracked in shared state) — so you're alerted once
per new breach, not every single day.
"""
import os
import requests
from html import escape


def _emails_to_check():
    raw = os.environ.get("EMAILS_TO_CHECK", "")
    return [e.strip() for e in raw.split(",") if e.strip()]


def get_section(state):
    emails = _emails_to_check()
    if not emails:
        return None  # nothing configured — silently skip

    known = state["breach_known"]
    new_alerts = []

    for email in emails:
        known.setdefault(email, [])
        try:
            resp = requests.get(f"https://api.xposedornot.com/v1/check-email/{email}", timeout=15)
            if resp.status_code == 404:
                continue  # no breaches on file for this email
            resp.raise_for_status()
            data = resp.json()
            breaches = data.get("breaches", [])
            # XposedOrNot nests breach names in a list of lists sometimes; flatten defensively
            flat = []
            for b in breaches:
                if isinstance(b, list):
                    flat.extend(b)
                else:
                    flat.append(b)

            new_for_email = [b for b in flat if b not in known[email]]
            if new_for_email:
                new_alerts.append((email, new_for_email))
                known[email].extend(new_for_email)
        except Exception as e:
            new_alerts.append((email, [f"(check failed: {str(e)[:50]})"]))

    state["breach_known"] = known

    if not new_alerts:
        return None  # nothing new — don't send a message

    lines = ["<b>🛡 New Data Breach Alert</b>", ""]
    for email, breach_list in new_alerts:
        lines.append(f"<b>{escape(email)}</b>")
        for b in breach_list:
            lines.append(f"  • {escape(str(b))}")
    return "\n".join(lines)
