"""
Telegram Daily Digest Bot
--------------------------
Consolidates all of Franklin's daily email automation projects into one
Telegram bot. Each topic is sent as its own separate message.

Topics: crypto prices, stock prices, forex rates, remote job matches,
tech news, data breach alerts, Catholic liturgical calendar, site uptime.
(Football news is intentionally excluded for now — needs a football-data.org
API key.)

Environment variables required (set as GitHub Actions secrets):
  TELEGRAM_BOT_TOKEN  - from @BotFather
  TELEGRAM_CHAT_ID    - your personal chat id (or a group/channel id)
  EMAILS_TO_CHECK     - comma-separated emails for the breach monitor (optional)
"""
from telegram_sender import send_message
from state_store import load_state, save_state

from modules import crypto, stocks, forex, jobs, tech_news, breach, catholic, uptime


def main():
    state = load_state()

    # ---- always-send sections (no state needed) ----
    always_on = [
        crypto.get_section,
        stocks.get_section,
        forex.get_section,
        tech_news.get_section,
        catholic.get_section,
    ]
    for get_section in always_on:
        text = get_section()
        if text:
            send_message(text)

    # ---- stateful, change/new-only sections ----
    jobs_text = jobs.get_section(state)
    if jobs_text:
        send_message(jobs_text)

    breach_text = breach.get_section(state)
    if breach_text:
        send_message(breach_text)

    uptime_text = uptime.get_section(state)
    if uptime_text:
        send_message(uptime_text)

    save_state(state)
    print("Digest run complete.")


if __name__ == "__main__":
    main()
