"""Stock prices: GOOG, AAPL, META, TSLA, NVDA, INTC, AMZN, NFLX.

Uses Yahoo Finance's public (keyless) chart endpoint. Note: SpaceX was
originally requested too, but it isn't publicly traded, so it's excluded.
"""
import requests
from html import escape

TICKERS = ["GOOG", "AAPL", "META", "TSLA", "NVDA", "INTC", "AMZN", "NFLX"]


def _fetch_one(ticker):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
    resp.raise_for_status()
    meta = resp.json()["chart"]["result"][0]["meta"]
    price = meta["regularMarketPrice"]
    prev_close = meta.get("chartPreviousClose") or meta.get("previousClose")
    change_pct = ((price - prev_close) / prev_close * 100) if prev_close else 0
    return price, change_pct


def get_section():
    lines = ["<b>📈 Stock Prices</b>", ""]
    any_ok = False
    for ticker in TICKERS:
        try:
            price, change_pct = _fetch_one(ticker)
            arrow = "▲" if change_pct >= 0 else "▼"
            lines.append(f"• <b>{ticker}</b>: ${price:,.2f}  {arrow} {abs(change_pct):.2f}%")
            any_ok = True
        except Exception as e:
            lines.append(f"• {ticker}: unavailable ({escape(str(e))[:40]})")
    if not any_ok:
        lines.append("\n⚠️ All tickers failed — Yahoo Finance may be rate-limiting this run.")
    return "\n".join(lines)
