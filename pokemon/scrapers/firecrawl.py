"""
Scraper using the Firecrawl API.

Firecrawl handles headless rendering, anti-bot measures, and rate
limiting for you.  It returns clean HTML that we then parse with the
same BeautifulSoup logic used by the other scraper, keeping the two
approaches comparable.

Requirements:
    Set FIRECRAWL_API_KEY in your environment or .env file.
    Get a key at https://firecrawl.dev.
"""

import os

import pandas as pd
from dotenv import load_dotenv

load_dotenv()

URL = "https://pokemondb.net/pokedex/all"


def scrape() -> pd.DataFrame:
    """Return the full Pokédex table as a DataFrame via Firecrawl."""
    api_key = os.environ.get("FIRECRAWL_API_KEY", "").strip()
    if not api_key:
        raise EnvironmentError(
            "FIRECRAWL_API_KEY is not set.\n"
            "Copy .env.example → .env and add your key from https://firecrawl.dev"
        )

    # Import here so missing firecrawl-py doesn't break the BeautifulSoup path
    from firecrawl import FirecrawlApp  # type: ignore[import]

    print(f"  Firecrawl → {URL}")
    app = FirecrawlApp(api_key=api_key)

    # Request clean HTML; Firecrawl handles JS rendering & bot detection.
    result = app.scrape(URL, formats=["html"])
    html: str = result.html  # type: ignore[union-attr]

    if not html:
        raise ValueError("Firecrawl returned no HTML — check your API key and quota.")

    # Reuse the same parsing logic to keep both scrapers directly comparable.
    from .beautifulsoup import _parse

    return _parse(html)
