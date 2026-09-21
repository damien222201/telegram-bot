"""Catholic feast-of-the-day lookup.

Movable feasts (tied to Easter) are computed via the Meeus/Jones/Butcher
algorithm. Fixed-date feasts use a curated dictionary of major solemnities
and feast days.

Note: this is a simplified calendar covering major solemnities/feasts and
all movable dates — it does not attempt full year-round saint-of-the-day
coverage the way a dedicated liturgical calendar project would.
"""
from datetime import date, timedelta
from html import escape

# ---- Fixed-date feasts (month, day) -> name ----
FIXED_FEASTS = {
    (1, 1): "Solemnity of Mary, Mother of God",
    (1, 6): "Epiphany of the Lord",
    (2, 2): "Presentation of the Lord",
    (3, 19): "Solemnity of St. Joseph",
    (3, 25): "Annunciation of the Lord",
    (4, 25): "St. Mark the Evangelist",
    (5, 1): "St. Joseph the Worker",
    (5, 31): "Visitation of the Blessed Virgin Mary",
    (6, 24): "Nativity of St. John the Baptist",
    (6, 29): "Solemnity of Sts. Peter and Paul",
    (7, 3): "St. Thomas the Apostle",
    (7, 22): "St. Mary Magdalene",
    (7, 25): "St. James the Apostle",
    (8, 6): "Transfiguration of the Lord",
    (8, 15): "Assumption of the Blessed Virgin Mary",
    (8, 24): "St. Bartholomew the Apostle",
    (9, 8): "Nativity of the Blessed Virgin Mary",
    (9, 14): "Exaltation of the Holy Cross",
    (9, 21): "St. Matthew the Apostle",
    (9, 29): "Sts. Michael, Gabriel and Raphael, Archangels",
    (10, 2): "The Holy Guardian Angels",
    (10, 18): "St. Luke the Evangelist",
    (10, 28): "Sts. Simon and Jude, Apostles",
    (11, 1): "Solemnity of All Saints",
    (11, 2): "All Souls' Day",
    (11, 9): "Dedication of the Lateran Basilica",
    (11, 30): "St. Andrew the Apostle",
    (12, 8): "Immaculate Conception of the Blessed Virgin Mary",
    (12, 12): "Our Lady of Guadalupe",
    (12, 25): "Nativity of the Lord (Christmas)",
    (12, 26): "St. Stephen, the First Martyr",
    (12, 27): "St. John the Apostle and Evangelist",
    (12, 28): "The Holy Innocents",
}


def _easter_date(year):
    """Meeus/Jones/Butcher Gregorian algorithm."""
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)


def _movable_feasts(year):
    easter = _easter_date(year)
    return {
        easter - timedelta(days=46): "Ash Wednesday",
        easter - timedelta(days=7): "Palm Sunday",
        easter - timedelta(days=3): "Holy Thursday",
        easter - timedelta(days=2): "Good Friday",
        easter - timedelta(days=1): "Holy Saturday",
        easter: "Easter Sunday — The Resurrection of the Lord",
        easter + timedelta(days=39): "Ascension of the Lord",
        easter + timedelta(days=49): "Pentecost Sunday",
        easter + timedelta(days=56): "Trinity Sunday",
        easter + timedelta(days=60): "Corpus Christi",
    }


def get_section():
    try:
        today = date.today()
        movable = _movable_feasts(today.year)

        feast_today = movable.get(today) or FIXED_FEASTS.get((today.month, today.day))

        lines = ["<b>✝️ Today in the Liturgical Calendar</b>", ""]
        lines.append(f"<i>{today.strftime('%A, %d %B %Y')}</i>")
        if feast_today:
            lines.append(f"\n<b>{escape(feast_today)}</b>")
        else:
            lines.append("\nFeria (weekday in Ordinary Time / current liturgical season) — no major fixed or movable feast today.")
        return "\n".join(lines)
    except Exception as e:
        return f"<b>✝️ Today in the Liturgical Calendar</b>\n⚠️ Failed to compute: {escape(str(e))}"
