"""
Pokémon Pokédex scraping → PCA → sprite scatter plot demo.

Usage
-----
    # BeautifulSoup (default, no API key required)
    uv run main.py

    # Firecrawl (requires FIRECRAWL_API_KEY in .env)
    uv run main.py --scraper firecrawl

    # Skip sprite download for a quick plain scatter
    uv run main.py --no-sprites
"""

import argparse
import sys

from pokemon import processing, sprites, visualization
from pokemon.scrapers import beautifulsoup, firecrawl


def main() -> None:
    args = _parse_args()

    # ── 1. Scrape ──────────────────────────────────────────────────────────
    print(f"\n[1/4] Scraping Pokédex with '{args.scraper}' …")
    try:
        df = beautifulsoup.scrape() if args.scraper == "beautifulsoup" else firecrawl.scrape()
    except EnvironmentError as exc:
        print(f"\nConfiguration error:\n  {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"      → {len(df)} entries scraped.")

    # ── 2. PCA ────────────────────────────────────────────────────────────
    print("\n[2/4] Applying PCA on battle stats …")
    df_pca = processing.apply_pca(df)

    # ── 3. Sprites ────────────────────────────────────────────────────────
    sprite_images = None
    if not args.no_sprites:
        print(f"\n[3/4] Downloading {len(df_pca)} sprites (cached after first run) …")
        sprite_images = sprites.download_all(df_pca)
    else:
        print("\n[3/4] Skipping sprite download (--no-sprites).")

    # ── 4. Visualise ──────────────────────────────────────────────────────
    print("\n[4/4] Rendering scatter plot …")
    visualization.scatter(df_pca, sprite_images)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Pokémon Pokédex scraping demo with PCA sprite visualization.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--scraper",
        choices=["beautifulsoup", "firecrawl"],
        default="beautifulsoup",
        help="HTTP backend to use (default: beautifulsoup)",
    )
    parser.add_argument(
        "--no-sprites",
        action="store_true",
        help="Render a plain coloured scatter plot without downloading sprites",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
