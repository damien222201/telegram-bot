"""Forex rates: USD, GBP, EUR, CAD to NGN, using the free open.er-api.com endpoint."""
import requests
from html import escape


def get_section():
    try:
        resp = requests.get("https://open.er-api.com/v6/latest/USD", timeout=15)
        resp.raise_for_status()
        data = resp.json()
        rates = data.get("rates", {})
        ngn = rates.get("NGN")
        gbp = rates.get("GBP")
        eur = rates.get("EUR")
        cad = rates.get("CAD")

        if not all([ngn, gbp, eur, cad]):
            raise ValueError("missing one or more required rates in API response")

        lines = ["<b>💱 Forex Rates (→ NGN)</b>", ""]
        lines.append(f"• <b>USD</b>: ₦{ngn:,.2f}")
        lines.append(f"• <b>GBP</b>: ₦{(ngn / gbp):,.2f}")
        lines.append(f"• <b>EUR</b>: ₦{(ngn / eur):,.2f}")
        lines.append(f"• <b>CAD</b>: ₦{(ngn / cad):,.2f}")
        return "\n".join(lines)
    except Exception as e:
        return f"<b>💱 Forex Rates (→ NGN)</b>\n⚠️ Failed to fetch: {escape(str(e))}"
