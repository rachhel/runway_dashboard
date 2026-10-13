# Reading the Runway

How Vogue Runway tells different stories of luxury fashion: a Streamlit dashboard and project webpage built on 13,983 Vogue Runway reviews (FashionDB, 1988–2025).

- **Live dashboard:** https://YOUR-APP.streamlit.app
- **Project webpage:** https://YOUR-USERNAME.github.io/YOUR-REPO/

## What's in this repo
| Path | What it is |
|---|---|
| `app.py` | The Streamlit dashboard (pages: The Story, Coverage, Review Length, Themes, Notes & Limits) |
| `runway_data.py` | Data loading, cleaning, theme tagging and quote extraction (same steps and keyword lists as the notebook) |
| `requirements.txt` | Python packages the dashboard needs |
| `.streamlit/config.toml` | Theme colours and settings |
| `static/fonts/` | Fonts used by the dashboard |
| `docs/` | The project webpage, published with GitHub Pages (`docs/index.html`, chart images in `docs/images/`) |

## Data
The dashboard downloads FashionDB directly from Hugging Face
(`hf://datasets/traopia/FashionDB/data_vogue_final.parquet`) and repeats the notebook's cleaning steps, so no data file is needed.
The cleaned CSV is not included because the reviews are Vogue's copyrighted writing.

If you have the notebook's export (`fashiondb_vogue_reviews_clean.csv`), you can place it next to `app.py` and the dashboard will use it instead of downloading.

## How to run the dashboard
Requires Python 3.10 or newer and an internet connection.

1. Open a terminal in this folder.
2. (Optional) Create a virtual environment:
   `python -m venv .venv` then `source .venv/bin/activate` (Mac) or `.venv\Scripts\activate` (Windows)
3. Install the packages:
   `pip install -r requirements.txt`
4. Start the dashboard:
   `streamlit run app.py`
5. It opens in your browser at http://localhost:8501. The first load takes a little longer while the data downloads.

## How to view the webpage locally
Open `docs/index.html` in a browser. The embedded dashboard and video need an internet connection.

## Notes
- Runway photos and review text © Vogue Runway; every review card links to the original review.
- An independent student project for DESIGNTK 530, not affiliated with Vogue or Condé Nast.
- AI assistance was used for code and drafting; see the project notebook for details.