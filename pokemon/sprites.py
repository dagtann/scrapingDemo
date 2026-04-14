"""
Sprite downloader with on-disk cache.

Downloads the small icon sprites for every Pokémon in the DataFrame
concurrently and caches them to .sprites/ so repeated runs are instant.
Falls back to the PokeAPI CDN sprite when the pokemondb URL is absent.
"""

import io
import concurrent.futures
import sys
from pathlib import Path
from typing import Optional

import requests
from PIL import Image

CACHE_DIR = Path(".sprites")
MAX_WORKERS = 30
TIMEOUT = 10
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; PokemonSpriteFetcher/1.0)"}


def download_all(df) -> dict[str, Optional[Image.Image]]:
    """
    Download sprites for every row in df, returning {Name: PIL.Image}.
    Uses a thread pool and shows a simple progress counter.
    """
    CACHE_DIR.mkdir(exist_ok=True)

    tasks = list(zip(df["Name"], df["sprite_url"], df["#"]))
    total = len(tasks)
    results: dict[str, Optional[Image.Image]] = {}
    done = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        future_to_name = {
            pool.submit(_fetch, name, url, num): name
            for name, url, num in tasks
        }
        for future in concurrent.futures.as_completed(future_to_name):
            name = future_to_name[future]
            done += 1
            try:
                results[name] = future.result()
            except Exception:
                results[name] = None
            _print_progress(done, total)

    print()  # newline after progress bar
    ok = sum(1 for v in results.values() if v is not None)
    print(f"  {ok}/{total} sprites loaded.")
    return results


# ── Internal helpers ──────────────────────────────────────────────────────────

def _fetch(name: str, sprite_url: str, dex_num: str) -> Optional[Image.Image]:
    cache_path = CACHE_DIR / f"{_safe_filename(name)}.png"

    if cache_path.exists():
        return Image.open(cache_path).convert("RGBA")

    url = sprite_url or _pokeapi_url(dex_num)
    if not url:
        return None

    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        img = Image.open(io.BytesIO(resp.content)).convert("RGBA")
        img.save(cache_path)
        return img
    except Exception:
        # Silently fall back to PokeAPI if the pokemondb URL fails
        fallback = _pokeapi_url(dex_num)
        if fallback and fallback != url:
            return _fetch(name, fallback, dex_num)
        return None


def _pokeapi_url(dex_num: str) -> Optional[str]:
    try:
        num = int(dex_num)
        return (
            f"https://raw.githubusercontent.com/PokeAPI/sprites"
            f"/master/sprites/pokemon/{num}.png"
        )
    except (ValueError, TypeError):
        return None


def _safe_filename(name: str) -> str:
    return "".join(c if c.isalnum() else "_" for c in name).lower()


def _print_progress(done: int, total: int) -> None:
    pct = done / total
    bar_len = 40
    filled = int(bar_len * pct)
    bar = "#" * filled + "-" * (bar_len - filled)
    sys.stdout.write(f"\r  [{bar}] {done}/{total}")
    sys.stdout.flush()
