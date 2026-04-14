"""
Scraper using requests + BeautifulSoup.

Fetches the raw HTML directly from pokemondb.net and parses the
#pokedex table with a CSS selector + BeautifulSoup traversal.
No external API is required.
"""

import requests
import pandas as pd
from bs4 import BeautifulSoup

URL = "https://pokemondb.net/pokedex/all"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def scrape() -> pd.DataFrame:
    """Return the full Pokédex table as a DataFrame."""
    print(f"  GET {URL}")
    response = requests.get(URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return _parse(response.text)


def _parse(html: str) -> pd.DataFrame:
    soup = BeautifulSoup(html, "lxml")
    table = soup.find("table", {"id": "pokedex"})
    if table is None:
        raise ValueError("Could not find #pokedex table on the page.")

    rows = []
    for tr in table.tbody.find_all("tr"):
        cells = tr.find_all("td")
        if len(cells) < 10:
            continue

        row = _parse_row(cells)
        if row:
            rows.append(row)

    return pd.DataFrame(rows)


def _parse_row(cells) -> dict | None:
    # ── Column 0: dex number + icon sprite ──────────────────────────────────
    num_cell = cells[0]
    img = num_cell.find("img")
    sprite_url = ""
    if img:
        # pokemondb uses protocol-relative URLs (//img.pokemondb.net/...)
        raw = img.get("src") or img.get("data-src") or ""
        sprite_url = ("https:" + raw) if raw.startswith("//") else raw
    dex_num = num_cell.get_text(strip=True)

    # ── Column 1: name ───────────────────────────────────────────────────────
    name_cell = cells[1]
    anchor = name_cell.find("a", class_="ent-name")
    name = anchor.get_text(strip=True) if anchor else name_cell.get_text(strip=True)

    # ── Column 2: type(s) ────────────────────────────────────────────────────
    type_links = cells[2].find_all("a")
    type1 = type_links[0].get_text(strip=True) if type_links else ""
    type2 = type_links[1].get_text(strip=True) if len(type_links) > 1 else ""

    # ── Columns 3-9: Total, HP, Attack, Defense, Sp.Atk, Sp.Def, Speed ──────
    stat_names = ["Total", "HP", "Attack", "Defense", "Sp. Atk", "Sp. Def", "Speed"]
    stats = {s: cells[3 + i].get_text(strip=True) for i, s in enumerate(stat_names)}

    return {
        "#": dex_num,
        "Name": name,
        "Type 1": type1,
        "Type 2": type2,
        "sprite_url": sprite_url,
        **stats,
    }
