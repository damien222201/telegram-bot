"""Remote job alerts matching target roles, via RemoteOK's free public API.

Only jobs not already seen (tracked in shared state) are reported, so you
don't get the same posting every day.
"""
import requests
from html import escape

TARGET_ROLES = ["ai engineer", "software engineer", "full stack", "full-stack", "data analyst"]


def get_section(state):
    try:
        resp = requests.get(
            "https://remoteok.com/api",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=15,
        )
        resp.raise_for_status()
        listings = resp.json()
        # RemoteOK's first array element is a metadata blob, not a job.
        listings = [j for j in listings if isinstance(j, dict) and j.get("id")]

        seen = set(state["jobs_seen"])
        new_matches = []
        for job in listings:
            job_id = str(job.get("id"))
            if job_id in seen:
                continue
            position = (job.get("position") or "").lower()
            tags = " ".join(job.get("tags") or []).lower()
            haystack = position + " " + tags
            if any(role in haystack for role in TARGET_ROLES):
                new_matches.append(job)

        # mark everything we looked at this run as seen, so old postings
        # never resurface even if they never matched
        for job in listings:
            seen.add(str(job.get("id")))
        state["jobs_seen"] = list(seen)[-2000:]  # keep the state file from growing forever

        if not new_matches:
            return None  # nothing new — don't send a message at all

        lines = ["<b>💼 New Remote Job Matches</b>", ""]
        for job in new_matches[:10]:
            title = escape(job.get("position", "Untitled role"))
            company = escape(job.get("company", "Unknown company"))
            url = job.get("url", "https://remoteok.com")
            lines.append(f"• <a href=\"{url}\">{title}</a> — {company}")
        if len(new_matches) > 10:
            lines.append(f"\n…and {len(new_matches) - 10} more new matches today.")
        return "\n".join(lines)
    except Exception as e:
        return f"<b>💼 New Remote Job Matches</b>\n⚠️ Failed to fetch: {escape(str(e))}"
