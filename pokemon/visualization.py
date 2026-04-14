"""
PCA scatter plot with Pokémon sprite avatars.

Each Pokémon is rendered at its (PC1, PC2) position using a miniature
sprite as the marker.  An underlying colour-coded scatter layer gives
the Type 1 legend even when sprites overlap.
"""

from typing import Optional

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from PIL import Image

# Official-ish colours for every main-series type
TYPE_COLORS: dict[str, str] = {
    "Normal":   "#A8A878",
    "Fire":     "#F08030",
    "Water":    "#6890F0",
    "Electric": "#F8D030",
    "Grass":    "#78C850",
    "Ice":      "#98D8D8",
    "Fighting": "#C03028",
    "Poison":   "#A040A0",
    "Ground":   "#E0C068",
    "Flying":   "#A890F0",
    "Psychic":  "#F85888",
    "Bug":      "#A8B820",
    "Rock":     "#B8A038",
    "Ghost":    "#705898",
    "Dragon":   "#7038F8",
    "Dark":     "#705848",
    "Steel":    "#B8B8D0",
    "Fairy":    "#EE99AC",
}

SPRITE_ZOOM = 0.40       # scale factor for icon sprites (~40 px wide)
OUTPUT_FILE = "pokemon_pca.png"


def scatter(df: pd.DataFrame, sprite_images: Optional[dict] = None) -> None:
    """
    Render a PCA scatter plot.

    Parameters
    ----------
    df:
        DataFrame with at least PC1, PC2, Name, and Type 1 columns.
    sprite_images:
        Mapping {Name: PIL.Image} returned by sprites.download_all().
        When None the plot shows plain coloured circles.
    """
    fig, ax = plt.subplots(figsize=(22, 16))
    _style_axes(ax, fig)

    # ── Base scatter layer (provides the coloured legend) ──────────────────
    all_types = sorted(df["Type 1"].dropna().unique())
    for ptype in all_types:
        mask = df["Type 1"] == ptype
        color = TYPE_COLORS.get(ptype, "#888888")
        ax.scatter(
            df.loc[mask, "PC1"],
            df.loc[mask, "PC2"],
            c=color,
            s=80,
            alpha=0.25 if sprite_images else 0.75,
            zorder=1,
            label=ptype,
        )

    # ── Sprite overlay ─────────────────────────────────────────────────────
    if sprite_images:
        _add_sprites(ax, df, sprite_images)

    # ── Axes labels & title ────────────────────────────────────────────────
    ax.set_xlabel("Principal Component 1  →  overall bulk & power", color="white", fontsize=12)
    ax.set_ylabel("Principal Component 2  →  offence vs. defence balance", color="white", fontsize=12)
    ax.set_title(
        "Pokémon Battle Stats — PCA Projection with Sprite Avatars",
        color="white", fontsize=16, pad=18, fontweight="bold",
    )

    # ── Type legend ────────────────────────────────────────────────────────
    handles = [
        mpatches.Patch(facecolor=TYPE_COLORS.get(t, "#888888"), label=t, edgecolor="white", linewidth=0.4)
        for t in all_types
    ]
    legend = ax.legend(
        handles=handles, title="Primary Type",
        ncol=2, loc="upper left", fontsize=9,
        facecolor="#0d0d1a", edgecolor="#445566",
        labelcolor="white", title_fontsize=10,
    )
    legend.get_title().set_color("white")

    plt.tight_layout()
    fig.savefig(OUTPUT_FILE, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    print(f"  Saved → {OUTPUT_FILE}")
    plt.show()


# ── Private helpers ────────────────────────────────────────────────────────────

def _add_sprites(ax, df: pd.DataFrame, sprite_images: dict) -> None:
    for _, row in df.iterrows():
        img: Optional[Image.Image] = sprite_images.get(row["Name"])
        if img is None:
            continue
        arr = np.array(img)
        imagebox = OffsetImage(arr, zoom=SPRITE_ZOOM)
        imagebox.image.axes = ax
        ab = AnnotationBbox(
            imagebox,
            (row["PC1"], row["PC2"]),
            frameon=False,
            pad=0,
            zorder=2,
        )
        ax.add_artist(ab)


def _style_axes(ax, fig) -> None:
    bg = "#1a1a2e"
    fg = "#16213e"
    ax.set_facecolor(bg)
    fig.patch.set_facecolor(fg)
    ax.tick_params(colors="white", labelsize=9)
    ax.xaxis.label.set_color("white")
    ax.yaxis.label.set_color("white")
    for spine in ax.spines.values():
        spine.set_edgecolor("#334455")
    ax.grid(color="#2a3a4a", linewidth=0.5, linestyle="--", alpha=0.6)
