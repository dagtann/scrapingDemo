"""
PCA dimensionality reduction on Pokémon battle stats.

The six base stats (HP, Attack, Defense, Sp. Atk, Sp. Def, Speed) are
standardised to zero mean / unit variance before PCA so that no single
stat dominates purely due to scale differences.
"""

import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

STAT_COLUMNS = ["HP", "Attack", "Defense", "Sp. Atk", "Sp. Def", "Speed"]


def apply_pca(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add PC1 and PC2 columns to df by running PCA on the battle stats.
    Rows with missing stats are dropped.
    """
    df = df.copy()

    for col in STAT_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=STAT_COLUMNS).reset_index(drop=True)

    X = df[STAT_COLUMNS].values
    X_scaled = StandardScaler().fit_transform(X)

    pca = PCA(n_components=2, random_state=42)
    components = pca.fit_transform(X_scaled)

    df["PC1"] = components[:, 0]
    df["PC2"] = components[:, 1]

    ratio = pca.explained_variance_ratio_
    print(
        f"  PC1 explains {ratio[0]:.1%} of variance, "
        f"PC2 explains {ratio[1]:.1%}  "
        f"(total: {sum(ratio):.1%})"
    )

    return df
