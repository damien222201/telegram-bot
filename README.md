# Telegram Daily Digest Bot

Consolidates all of your daily email automation projects into one Telegram bot. Each topic arrives as its own separate message, run daily for free on GitHub Actions.

## What it sends

| Topic | Source | Behavior |
|---|---|---|
| 💰 Crypto prices | CoinGecko (free, no key) | BTC, ETH, BNB, PI, TON, USDT — USD + NGN, 24h change. Sent daily. |
| 📈 Stock prices | Yahoo Finance public endpoint (no key) | GOOG, AAPL, META, TSLA, NVDA, INTC, AMZN, NFLX. Sent daily. |
| 💱 Forex rates | open.er-api.com (free, no key) | USD, GBP, EUR, CAD → NGN. Sent daily. |
| 🗞 Tech news | Hacker News (Algolia), dev.to, GitHub Trending | Daily digest; automatically becomes a weekly recap every Sunday. |
| ✝️ Liturgical calendar | Computed locally (Meeus/Jones/Butcher algorithm) + curated feast list | Sent daily. |
| 💼 Remote job matches | RemoteOK (free, no key) | Only **new** matches you haven't been alerted on before. Silent if nothing new. |
| 🛡 Breach alerts | XposedOrNot (free, no key) | Only **new** breaches per monitored email. Silent if nothing new. |
| 🚦 Uptime watcher | Direct HTTP checks on your GitHub Pages sites | Only sent when a site's status **changes** (up→down or back up). Silent otherwise. |

**Not included yet:** football scores — that needs a free football-data.org API key. Easy to add later (see "Adding football back" below).

## Why some messages don't show up every day

Jobs, breach alerts, and uptime are **change/new-only** by design — nobody wants the same job posting or "still up" message every single morning. The bot remembers what it already told you in `state/bot_state.json`, which the GitHub Actions workflow commits back to the repo after every run.

## Setup

1. **Create a Telegram bot:**
   - Message [@BotFather](https://t.me/BotFather) on Telegram → `/newbot` → follow the prompts → copy the bot token it gives you.

2. **Get your chat ID:**
   - Message your new bot anything (e.g. "hi").
   - Visit `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates` in a browser.
   - Find `"chat":{"id": ...}` in the response — that number is your `TELEGRAM_CHAT_ID`.

3. **Add repo secrets** (Settings → Secrets and variables → Actions):
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
   - `EMAILS_TO_CHECK` — comma-separated list of emails to breach-check (optional; skips that section if unset)

4. **Push this repo to GitHub.** The workflow runs daily at 05:00 UTC (06:00 UTC+1), or trigger it manually from the Actions tab (`workflow_dispatch`) to test.

## Running locally

```bash
pip install -r requirements.txt
export TELEGRAM_BOT_TOKEN="123456:ABC-your-token"
export TELEGRAM_CHAT_ID="123456789"
export EMAILS_TO_CHECK="you@email.com,other@email.com"
python main.py
```

Note: running locally won't persist state anywhere except your local `state/bot_state.json` — that's fine for testing, just don't commit test-run state changes over the real repo's state by accident.

## Project structure

```
main.py                  # orchestrates all modules, sends each as its own message
telegram_sender.py        # shared Telegram sendMessage helper (handles long message splitting)
state_store.py            # shared read/write for state/bot_state.json
modules/
  crypto.py
  stocks.py
  forex.py
  jobs.py
  tech_news.py
  breach.py
  catholic.py
  uptime.py
state/bot_state.json      # persisted state — committed back by the workflow after each run
```

## Adding football back

1. Get a free API key at [football-data.org](https://www.football-data.org/client/register).
2. Add it as a repo secret, e.g. `FOOTBALL_DATA_API_KEY`.
3. Create `modules/football.py` with a `get_section()` function that calls the `/v4/competitions/{code}/matches` endpoint (competition codes: `PL`, `PD`, `SA`, `BL1`, `FL1` for the top 5 leagues) with an `X-Auth-Token` header, and returns an HTML-formatted string the same way the other modules do.
4. Import and call it in `main.py`'s `always_on` list.

## Customizing

- **Add/remove a topic:** each module exposes a `get_section()` (or `get_section(state)` for stateful ones) returning an HTML string, or `None` to skip sending. Add a new file in `modules/` and wire it into `main.py`.
- **Change send time:** edit the cron expression in `.github/workflows/telegram-digest.yml` (always UTC).
- **Change tracked tickers/coins/sites:** edit the relevant constant at the top of each module file.

## License

MIT.
