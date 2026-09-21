"""Tech news: Hacker News, dev.to, GitHub Trending. Weekly recap on Sundays."""
from datetime import datetime, timedelta, timezone
from html import escape
import requests

ITEMS_PER_SOURCE = 5
HEADERS = {"User-Agent": "Mozilla/5.0 (telegram-digest-bot)"}


def _is_sunday():
    local = datetime.now(timezone.utc) + timedelta(hours=1)  # UTC+1
    return local.weekday() == 6


def _fetch_hn(days):
    since_ts = int((datetime.now(timezone.utc) - timedelta(days=days)).timestamp())
    url = "https://hn.algolia.com/api/v1/search_by_date"
    params = {"tags": "story", "numericFilters": f"created_at_i>{since_ts}", "hitsPerPage": 100}
    resp = requests.get(url, params=params, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    hits = resp.json().get("hits", [])
    hits.sort(key=lambda h: h.get("points", 0), reverse=True)
    return [
        {
            "title": h.get("title") or "(untitled)",
            "url": h.get("url") or f"https://news.ycombinator.com/item?id={h.get('objectID')}",
            "points": h.get("points", 0),
        }
        for h in hits[:ITEMS_PER_SOURCE]
    ]


def _fetch_devto(days):
    url = "https://dev.to/api/articles"
    resp = requests.get(url, params={"top": days, "per_page": ITEMS_PER_SOURCE}, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    return [
        {"title": a.get("title", "(untitled)"), "url": a.get("url", "#"), "points": a.get("positive_reactions_count", 0)}
        for a in resp.json()[:ITEMS_PER_SOURCE]
    ]


def _fetch_github_trending(weekly):
    from bs4 import BeautifulSoup
    params = {"since": "weekly"} if weekly else {}
    resp = requests.get("https://github.com/trending", params=params, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    items = []
    for repo in soup.select("article.Box-row")[:ITEMS_PER_SOURCE]:
        link = repo.select_one("h2 a")
        if not link:
            continue
        path = link.get("href", "").strip("/")
        stars_el = repo.select_one('a[href$="/stargazers"]')
        items.append({
            "title": path,
            "url": f"https://github.com/{path}",
            "stars": stars_el.get_text(strip=True) if stars_el else "?",
        })
    return items


def get_section():
    weekly = _is_sunday()
    days = 7 if weekly else 1
    period = "This Week's" if weekly else "Today's"

    lines = [f"<b>🗞 {period} Tech Digest</b>", ""]

    try:
        lines.append("<b>Hacker News</b>")
        for i in _fetch_hn(days):
            lines.append(f"• <a href=\"{i['url']}\">{escape(i['title'])}</a> (▲{i['points']})")
    except Exception as e:
        lines.append(f"⚠️ Hacker News failed: {escape(str(e))[:60]}")

    lines.append("")
    try:
        lines.append("<b>dev.to</b>")
        for i in _fetch_devto(days):
            lines.append(f"• <a href=\"{i['url']}\">{escape(i['title'])}</a> (♥{i['points']})")
    except Exception as e:
        lines.append(f"⚠️ dev.to failed: {escape(str(e))[:60]}")

    lines.append("")
    try:
        lines.append("<b>GitHub Trending</b>")
        for i in _fetch_github_trending(weekly):
            lines.append(f"• <a href=\"{i['url']}\">{escape(i['title'])}</a> (★{i['stars']})")
    except Exception as e:
        lines.append(f"⚠️ GitHub Trending failed: {escape(str(e))[:60]}")

    return "\n".join(lines)
