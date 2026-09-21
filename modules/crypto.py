"""Crypto prices: Bitcoin, Ethereum, BNB, Pi, TON, USDT — USD and NGN, with 24h change."""
import requests
from html import escape

COINS = {
    "bitcoin": "Bitcoin (BTC)",
    "ethereum": "Ethereum (ETH)",
    "binancecoin": "BNB",
    "pi-network": "Pi Network (PI)",
    "the-open-network": "Toncoin (TON)",
    "tether": "Tether (USDT)",
}


def get_section():
    try:
        ids = ",".join(COINS.keys())
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": ids,
            "vs_currencies": "usd,ngn",
            "include_24hr_change": "true",
        }
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        lines = ["<b>💰 Crypto Prices</b>", ""]
        for coin_id, label in COINS.items():
            info = data.get(coin_id)
            if not info:
                lines.append(f"• {escape(label)}: data unavailable")
                continue
            usd = info.get("usd")
            ngn = info.get("ngn")
            change = info.get("usd_24h_change", 0) or 0
            arrow = "▲" if change >= 0 else "▼"
            lines.append(
                f"• <b>{escape(label)}</b>: ${usd:,.2f} / ₦{ngn:,.0f}  "
                f"{arrow} {abs(change):.2f}% (24h)"
            )
        return "\n".join(lines)
    except Exception as e:
        return f"<b>💰 Crypto Prices</b>\n⚠️ Failed to fetch: {escape(str(e))}"
