"""Data helpers for The Runway Index dashboard.

Everything here is plain pandas, so it can be tested without Streamlit.
The theme word lists are the same ones used in the analysis notebook.
"""

import re
from pathlib import Path

import pandas as pd

DATA_FILE = Path(__file__).parent / "fashiondb_vogue_reviews_cleans.csv"

# Fixed order and colours for the four collection types (validated for colour-blind separation).
ORDER = ["couture", "ready-to-wear", "menswear", "pre-collections"]
COLORS = {
    "couture": "#9E2A3A",          # oxblood
    "ready-to-wear": "#2563A8",    # ink blue
    "menswear": "#2E8A57",         # green
    "pre-collections": "#C08A12",  # ochre
}
LABELS = {
    "couture": "Couture",
    "ready-to-wear": "Ready-to-Wear",
    "menswear": "Menswear",
    "pre-collections": "Pre-Collections",
}
DESCRIPTIONS = {
    "couture": "Made-to-measure clothes from the Paris couture houses, shown twice a year.",
    "ready-to-wear": "The main womenswear collections, shown each spring and fall.",
    "menswear": "Men's collections, shown on their own calendar each season.",
    "pre-collections": "Resort and pre-fall: smaller collections shown between the main seasons.",
}

THEMES = {
    "craft": ("Unique Craft", ["embroider", "handmade", "hand-", "atelier", "craft", "artisan", "beaded", "beading"]),
    "tailoring": ("Sharp Tailoring", ["tailor", "suiting", "blazer", "lapel", "pinstripe", "trouser"]),
    "romance": ("Romantic", ["romantic", "romance", "dream", "fairy", "ethereal", "delicate"]),
    "real-life dressing": ("Everyday Dressing", ["wearable", "customer", "everyday", "practical", "wardrobe", "commercial"]),
    "heritage": ("House Heritage", ["archive", "heritage", "founder", "legacy", "tradition", "house code"]),
    "clientele": ("Clientele", ["client"]),
    "experimentation": ("Experimental", ["experiment", "avant-garde", "conceptual", "deconstruct", "radical", "innovat"]),
}
BROWSE_THEMES = ["craft", "tailoring", "romance", "real-life dressing", "heritage"]


def theme_pattern(theme):
    """Regex matching any of a theme's words at the start of a word."""
    return r"\b(?:" + "|".join(THEMES[theme][1]) + ")"


HF_FILE = "hf://datasets/traopia/FashionDB/data_vogue_final.parquet"
MAIN_TYPES = ["couture", "ready-to-wear", "menswear", "resort", "pre-fall"]


def clean_raw(raw):
    """Repeat the notebook's cleaning on the raw FashionDB show table."""
    df = raw.copy()
    category = df["category"].fillna("")
    blank = category == ""
    df["collection_type"] = category
    df.loc[blank & (df["season"] == "resort"), "collection_type"] = "resort"      # Resort is only labelled in season.
    df.loc[blank & (df["season"] == "pre-fall"), "collection_type"] = "pre-fall"  # Pre-fall is only labelled in season.
    df = df[df["collection_type"].isin(MAIN_TYPES)].copy()                         # Drops bridal and regional shows.
    text = df["description"].fillna("")
    placeholder = text.str.contains("did not review", case=False)
    empty = text.str.split().str.len().fillna(0) == 0
    df = df[~placeholder & ~empty].copy()                                          # Drops shows with no real review.
    df["n_looks"] = df["image_urls"].apply(lambda x: 0 if x is None else len(x))  # Number of runway photos.
    df["review_words"] = df["description"].fillna("").str.split().str.len()       # Review length in words.
    df = df.rename(columns={"description": "review_text", "editor": "reviewer", "URL": "show_url"})
    df["record"] = df.index                                                        # Same record numbers as the notebook.
    return df.drop(columns=["image_urls", "image_urls_sample"], errors="ignore")


def load_raw_from_hub():
    """Download the show table straight from Hugging Face (used when no local CSV is present)."""
    return pd.read_parquet(HF_FILE)


def load_data(path=DATA_FILE):
    """Use the notebook's cleaned CSV if it is next to the app; otherwise load and clean the data from Hugging Face."""
    if Path(path).exists():
        df = pd.read_csv(path)
        if "record" not in df.columns:
            df = df.reset_index().rename(columns={"index": "record"})
    else:
        df = clean_raw(load_raw_from_hub())
    df["review_text"] = df["review_text"].fillna("").astype(str)
    df["year"] = df["year"].astype(int)
    if "collection_group" not in df.columns:
        df["collection_group"] = df["collection_type"].replace({"resort": "pre-collections", "pre-fall": "pre-collections"})
    df = df[df["collection_group"].isin(ORDER)].copy()
    lower = df["review_text"].str.lower()
    for theme in THEMES:
        col = "theme_" + theme
        if col in df.columns:
            df[col] = df[col].astype(str).str.lower().isin(["true", "1"])
        else:
            df[col] = lower.str.contains(theme_pattern(theme), regex=True)
    if "cover_image_url" not in df.columns:
        df["cover_image_url"] = ""
    df["cover_image_url"] = df["cover_image_url"].fillna("").astype(str)
    df["season_label"] = df.apply(season_label, axis=1)
    return df


def season_label(row):
    """Readable label such as 'Resort 2017' or 'Fall 2015 Menswear'."""
    show = str(row.get("show", ""))
    if show and show != "nan":
        return show.replace("-", " ").title().replace("Ready To Wear", "Ready-to-Wear").replace("Pre Fall", "Pre-Fall")
    return f"{str(row.get('season', '')).title()} {row.get('year', '')}"


def theme_table(df):
    """Percentage of reviews mentioning each theme, rows = themes, columns = collection types."""
    cols = ["theme_" + t for t in THEMES]
    pct = df.groupby("collection_group")[cols].mean().T * 100
    pct = pct.reindex(columns=[c for c in ORDER if c in pct.columns])
    pct.index = [THEMES[t][0] for t in THEMES]
    return pct.round(1)


def excerpt(text, theme=None, max_words=34):
    """First sentence that mentions the theme (or the first sentence), trimmed to max_words."""
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    chosen = sentences[0] if sentences else ""
    pattern = re.compile(theme_pattern(theme), re.IGNORECASE) if theme else None
    if pattern:
        for sentence in sentences:
            if pattern.search(sentence):
                chosen = sentence
                break
    words = chosen.split()
    if len(words) <= max_words:
        return chosen
    # Keep the theme word inside the trimmed window so the quote shows why the show matched.
    start = 0
    if pattern:
        hit = next((i for i, w in enumerate(words) if pattern.search(w)), 0)
        start = max(0, min(hit - max_words // 3, len(words) - max_words))
    clip = " ".join(words[start:start + max_words]).rstrip(",;:")
    return ("…" if start > 0 else "") + clip + ("…" if start + max_words < len(words) else "")


def top_houses(df, n=15):
    """Names of the n houses with the most reviewed shows."""
    return df["fashion_house"].value_counts().head(n).index.tolist()


def summary_by_group(df):
    """Shows, median review length and median photo count for each collection type."""
    out = df.groupby("collection_group").agg(
        shows=("record", "size"),
        median_words=("review_words", "median"),
        median_looks=("n_looks", "median"),
    )
    return out.reindex([c for c in ORDER if c in out.index])