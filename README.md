# The Runway Index — dashboard

An editorial Streamlit dashboard of 13,983 Vogue Runway reviews (FashionDB, 1988–2025).

## Files
- `app.py` — the dashboard (five tabs: The Story, Four Collections, Discover by Theme, The Evidence, Notes & Limits)
- `runway_data.py` — data loading, theme tagging and quote extraction (same keyword lists as the notebook)
- `requirements.txt` — Python packages
- `.streamlit/config.toml` — colours and fonts
- `fashiondb_vogue_reviews_clean.csv` — the cleaned data exported from the notebook (add this yourself)

## How to open it
1. Put `fashiondb_vogue_reviews_clean.csv` (exported from the notebook) in this folder, next to `app.py`.
2. Open a terminal in this folder and install the packages:
   `pip install -r requirements.txt`
3. Start the dashboard:
   `streamlit run app.py`
4. It opens in your browser at http://localhost:8501. Use full-screen (F11 / Ctrl+Cmd+F) when presenting.

## Notes
- Runway photos appear only if the CSV includes the `cover_image_url` column. Without it, cards show the house name instead.
- Photos load from Vogue's servers and need an internet connection. Photos and review text © Vogue Runway; every card links to the original review.
- The dashboard is an independent student project and is not affiliated with Vogue or Condé Nast.
