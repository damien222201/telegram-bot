"""Shared helper for sending messages to Telegram."""
import os
import time
import requests

TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"
MAX_LEN = 4000  # stay safely under Telegram's 4096 char limit


def _chunks(text, size=MAX_LEN):
    """Split long text on line breaks so we never cut a line in half."""
    if len(text) <= size:
        return [text]
    lines = text.split("\n")
    chunks, current = [], ""
    for line in lines:
        if len(current) + len(line) + 1 > size:
            chunks.append(current)
            current = line
        else:
            current = current + "\n" + line if current else line
    if current:
        chunks.append(current)
    return chunks


def send_message(text):
    """Send one topic's message to Telegram. Splits automatically if too long."""
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    url = TELEGRAM_API.format(token=token)

    for chunk in _chunks(text):
        resp = requests.post(url, json={
            "chat_id": chat_id,
            "text": chunk,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }, timeout=15)
        if not resp.ok:
            print(f"[warn] Telegram send failed: {resp.status_code} {resp.text}")
        time.sleep(0.4)  # be gentle on Telegram's rate limits between chunks
