"""Reading the Runway: an editorial dashboard of Vogue Runway reviews (FashionDB, 1988-2025).

Run with:  streamlit run app.py
"""

import html

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from runway_data import (
    COLORS, DESCRIPTIONS, LABELS, ORDER, THEMES,
    load_data, summary_by_group, theme_table,
)

st.set_page_config(page_title="Reading the Runway", layout="wide", initial_sidebar_state="collapsed")

# ----------  styling ----------
PAPER, INK, MUTED, RULE, ACCENT = "#F7F4EE", "#141414", "#6B6560", "#D9D3C7", "#9E2A3A"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Jost:wght@300;400;500&display=swap');
@font-face {{ font-family: 'Nimbus Sans'; src: url('app/static/fonts/NimbusSans-Regular.otf') format('opentype'); font-weight: 400; font-style: normal; font-display: swap; }}
@font-face {{ font-family: 'Nimbus Sans'; src: url('app/static/fonts/NimbusSans-Italic.otf') format('opentype'); font-weight: 400; font-style: italic; font-display: swap; }}
@font-face {{ font-family: 'Nimbus Sans'; src: url('app/static/fonts/NimbusSans-Bold.otf') format('opentype'); font-weight: 700; font-style: normal; font-display: swap; }}
@font-face {{ font-family: 'Nimbus Sans'; src: url('app/static/fonts/NimbusSans-BoldItalic.otf') format('opentype'); font-weight: 700; font-style: italic; font-display: swap; }}
.stApp {{ background: {PAPER}; color: {INK}; overflow-x: hidden; }}
header[data-testid="stHeader"], footer, #MainMenu {{ display: none; }}
.block-container {{ max-width: 1280px; padding-top: 1.5rem; padding-bottom: 4rem; }}
html, body, .stApp, p, li, label {{ font-family: 'Helvetica Neue', Helvetica, 'Nimbus Sans', sans-serif; }}
p, li {{ font-size: 1rem; line-height: 1.6; }}
h1, h2, h3 {{ font-family: 'Jost', sans-serif !important; font-weight: 400 !important; font-size: .95rem !important; letter-spacing: .18em; text-transform: uppercase; color: {INK}; }}

/* Centred title masthead */
.masthead {{ text-align: center; border-bottom: 1px solid {INK}; padding-bottom: .8rem; margin-bottom: .2rem; }}
.masthead .title {{ font-family: 'Helvetica Neue', Helvetica, 'Nimbus Sans', sans-serif; font-size: clamp(2rem, 6vw, 5rem); font-weight: 500; letter-spacing: .04em; line-height: 1; white-space: nowrap; }}
.masthead .strap {{ font-family: 'Jost', sans-serif; font-size: .78rem; letter-spacing: .32em; text-transform: uppercase; color: {MUTED}; margin-top: .6rem; }}

/* Centred uppercase tabs */
.stTabs [data-baseweb="tab-list"], .stTabs [role="tablist"] {{ display: flex; justify-content: center !important; width: 100%; gap: 2.2rem; border-bottom: 1px solid {RULE}; }}
.stTabs [data-baseweb="tab-list"] > button {{ flex: 0 0 auto; }}.stTabs button, .stTabs button * {{ font-family: 'Jost', sans-serif !important; font-size: .78rem !important; letter-spacing: .18em; text-transform: uppercase; color: {INK}; }}
div[data-baseweb="tab-highlight"] {{ background-color: {INK} !important; height: 1px !important; }}
div[data-baseweb="tab-border"] {{ display: none; }}

/* Section titles: small label, then a light uppercase headline, both centred */
.kicker {{ font-family: 'Jost', sans-serif; font-weight: 500; font-size: .75rem; letter-spacing: .22em; text-transform: uppercase; color: {INK}; text-align: center; margin-top: 2.5rem; }}
.kicker.section {{ margin-top: 4rem; margin-bottom: .4rem; }}
.headline {{ font-family: 'Jost', sans-serif; font-weight: 300; font-size: clamp(1.4rem, 2.4vw, 2rem); letter-spacing: .06em; text-transform: uppercase; line-height: 1.3; text-align: center; max-width: 56rem; margin: .5rem auto 1rem; }}
.headline.sm {{ font-size: clamp(1.3rem, 2.2vw, 1.8rem); }}
.dek {{ font-size: 1rem; color: {MUTED}; text-align: center; max-width: 40rem; margin: 0 auto 2.5rem; }}

/* Numbers, questions, findings */
.stat {{ border-top: 1px solid {RULE}; padding-top: .9rem; }}
.stat .num {{ font-family: 'Jost', sans-serif; font-weight: 300; font-size: 3.4rem; line-height: 1; }}
.stat .qtext {{ font-size: 1.1rem; line-height: 1.4; margin-top: .5rem; }}
.stat .lbl {{ font-family: 'Jost', sans-serif; font-size: .7rem; letter-spacing: .16em; text-transform: uppercase; color: {MUTED}; margin-top: .4rem; line-height: 1.5; }}
.stat.finding {{ padding-top: 1rem; margin-bottom: 1.8rem; }}
.stat.finding p {{ margin-top: .6rem; max-width: 34rem; }}
.pull {{ font-family: 'Jost', sans-serif; font-weight: 300; font-size: 1.35rem; line-height: 1.4; margin: 1rem 0 .4rem; }}
.cite {{ font-family: 'Jost', sans-serif; font-size: .68rem; letter-spacing: .16em; text-transform: uppercase; color: {MUTED}; }}
.population {{ font-family: 'Jost', sans-serif; font-size: .7rem; letter-spacing: .04em; color: #8A8A8A; margin: .6rem 0 1rem; }}
.count {{ font-family: 'Jost', sans-serif; font-size: .78rem; letter-spacing: .06em; color: #555; text-align: center; margin: .4rem 0 1.4rem; }}

.stRadio label p, .stMultiSelect label p, .stSlider label p {{ font-family: 'Jost', sans-serif; font-size: .75rem; letter-spacing: .14em; text-transform: uppercase; }}
hr {{ border-color: {RULE}; }}

/* Notes & Limits */
.note-head {{ font-family: 'Jost', sans-serif; font-size: .7rem; letter-spacing: .16em; text-transform: uppercase; color: {INK}; margin-top: .5rem; }}
.note-step {{ border-top: 1px solid {INK}; padding-top: 1rem; margin-bottom: 2rem; }}
.note-step .n {{ font-family: 'Jost', sans-serif; font-weight: 300; font-size: 2.4rem; line-height: 1; color: {ACCENT}; }}
.note-step p {{ font-size: .95rem; margin-top: .5rem; }}
.type-card {{ border-top: 3px solid; padding-top: .9rem; margin-bottom: 1.5rem; }}
.type-card .meta {{ font-family: 'Jost', sans-serif; font-size: .7rem; letter-spacing: .12em; text-transform: uppercase; color: {MUTED}; margin-top: .6rem; }}
.type-card p {{ font-size: .95rem; margin-top: .4rem; }}
.theme-row {{ display: grid; grid-template-columns: minmax(9rem, 12rem) 1fr; gap: 1rem; align-items: baseline; border-top: 1px solid {RULE}; padding: .8rem 0; }}
.chip {{ display: inline-block; font-family: 'Jost', sans-serif; font-size: .75rem; letter-spacing: .04em; border: 1px solid {RULE}; background: #FFFDF9; padding: .15rem .55rem; margin: .15rem .3rem .15rem 0; }}
.limits {{ columns: 2; column-gap: 3rem; padding-left: 1.2rem; }}
.limits li {{ margin-bottom: .7rem; break-inside: avoid; }}
@media (max-width: 760px) {{ .limits {{ columns: 1; }} }}
.prose p {{ font-size: .98rem; margin-top: .5rem; }}
.prose a, .source a {{ color: {ACCENT}; text-decoration: none; border-bottom: 1px solid {ACCENT}; }}
.source {{ font-family: 'Jost', sans-serif; font-size: .72rem; letter-spacing: .06em; color: {MUTED}; text-align: center; border-top: 1px solid {RULE}; padding-top: 1.2rem; margin-top: 3rem; }}
@media (max-width: 640px) {{ .theme-row {{ grid-template-columns: 1fr; gap: .3rem; }} }}
</style>
""", unsafe_allow_html=True)


def chart_style(fig, height=420):
    """Shared quiet chart styling: no background, thin recessive grid, sans-serif labels."""
    fig.update_layout(
        height=height, margin=dict(l=10, r=10, t=30, b=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Jost, sans-serif", size=13, color=INK),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, title=dict(text="")),
        hoverlabel=dict(bgcolor="#FFFDF9", font=dict(family="Jost, sans-serif"), bordercolor=RULE),
    )
    fig.update_xaxes(showgrid=False, linecolor=INK, ticks="outside", tickcolor=RULE)
    fig.update_yaxes(gridcolor="#E7E1D6", zeroline=False, linecolor=RULE)
    return fig


def show_chart(fig):
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})


def population(text):
    st.markdown(f'<div class="population">{html.escape(text)}</div>', unsafe_allow_html=True)


# ---------- Data ----------
@st.cache_data
def get_data():
    return load_data()


try:
    df = get_data()
except FileNotFoundError:
    st.error("Data file not found. Put fashiondb_vogue_reviews_clean.csv in the same folder as app.py, then reload.")
    st.stop()

N_ALL = len(df)
N_HOUSES = df["fashion_house"].nunique()
YEAR_MIN, YEAR_MAX = int(df["year"].min()), int(df["year"].max())
THEME_PCT = theme_table(df)
SUMMARY = summary_by_group(df)
ALL_POP = f"Based on all {N_ALL:,} reviewed shows, {YEAR_MIN}–{YEAR_MAX}. Does not change with filters."

# ---------- head ----------
st.markdown(
    f'<div class="masthead"><div class="title">READING THE RUNWAY</div>'
    f'<div class="strap">How Vogue Runway Tells Different Stories of Luxury Fashion </div></div>',
    unsafe_allow_html=True)

tab_story, tab_cov, tab_len, tab_themes, tab_notes = st.tabs(
    ["The Story", "1 · Coverage", "2 · Review Length", "3 · Themes", "Notes & Limits"])


def filters(prefix, default_years=None):
    """Collection-type and year filters, centred under the page question."""
    _, a, b, _ = st.columns([0.4, 3.2, 1.8, 0.4], gap="large")  # Empty columns on each side push the filters to the middle.
    with a:
        types = st.multiselect("Collection types", ORDER, default=ORDER, format_func=lambda c: LABELS[c], key=prefix + "_types")
    with b:
        years = st.slider("Season years", YEAR_MIN, YEAR_MAX, default_years or (YEAR_MIN, YEAR_MAX), key=prefix + "_years")
    sel = df[df["collection_group"].isin(types) & df["year"].between(*years)]
    shown = [t for t in ORDER if t in types]
    label = f"{', '.join(LABELS[t] for t in shown) or 'no collection type'} · {years[0]}–{years[1]}"
    return sel, shown, label


def selection_line(sel, label, noun="reviewed shows"):
    st.markdown(f'<div class="count">This view uses <b>{len(sel):,}</b> {noun} — {html.escape(label)}</div>', unsafe_allow_html=True)


# ---------- The Story ----------
with tab_story:
    craft_c = THEME_PCT.loc["Unique Craft", "couture"]
    tail_m = THEME_PCT.loc["Sharp Tailoring", "menswear"]
    every_p = THEME_PCT.loc["Everyday Dressing", "pre-collections"]
    st.markdown('<div class="kicker">The question</div>', unsafe_allow_html=True)
    st.markdown('<div class="headline sm">How do Vogue Runway’s reviews differ across couture, ready-to-wear, menswear and pre-collections?</div>',
                unsafe_allow_html=True)
    q1, q2, q3 = st.columns(3, gap="large")
    for col, num, q in [(q1, "1", "How is coverage spread across collection types, houses and years?"),
                        (q2, "2", "How does review length vary across collection types?"),
                        (q3, "3", "What themes set the collection types apart?")]:
        col.markdown(f'<div class="stat"><div class="lbl">Question {num}</div><div class="qtext">{q}</div></div>', unsafe_allow_html=True)

    # Objectives
    st.markdown('<div class="kicker section">Objectives</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="prose" style="max-width:46rem;margin:0 auto;text-align:center">'
        '<p>I want to find out whether Vogue Runway covers and describes collection types differently, using both numbers and the review text. '
        'I also want to turn what I find into an idea for improving how show reviews are presented to readers.</p></div>',
        unsafe_allow_html=True)

    # The four collection types
    st.markdown('<div class="kicker section">The four collection types</div>', unsafe_allow_html=True)
    for col, t in zip(st.columns(4, gap="large"), ORDER):
        n_houses = df.loc[df["collection_group"] == t, "fashion_house"].nunique()
        col.markdown(f'<div class="type-card" style="border-top-color:{COLORS[t]}"><div class="note-head">{LABELS[t]}</div>'
                     f'<p>{DESCRIPTIONS[t]}</p><div class="meta">{int(SUMMARY.loc[t, "shows"]):,} shows · {n_houses} houses</div></div>',
                     unsafe_allow_html=True)

    st.markdown('<div class="kicker section">What I found</div>', unsafe_allow_html=True)
    findings = [
        ("Coverage is uneven",
         f"Ready-to-wear is {SUMMARY.loc['ready-to-wear','shows'] / N_ALL * 100:.0f}% of all reviews and couture only "
         f"{SUMMARY.loc['couture','shows'] / N_ALL * 100:.0f}%. Menswear and pre-collections only appear in large numbers after the mid-2000s."),
        ("Couture and menswear get the most space",
         f"The typical couture review runs {SUMMARY.loc['couture','median_words']:.0f} words and menswear "
         f"{SUMMARY.loc['menswear','median_words']:.0f}; pre-collections about {SUMMARY.loc['pre-collections','median_words']:.0f}."),
        ("Each type has its own vocabulary",
         "Couture is described through how it is made, menswear through its cut, and pre-collections through wearibility and commerce. "
         "Experimentation is mentioned about equally everywhere."),
        ("What it means",
         "Vogue tells a different kind of story for each type of collection, so readers, brands and writers meet each one through a different lens."),
    ]
    for row in (findings[:2], findings[2:]):
        for col, (head, text) in zip(st.columns(2, gap="large"), row):
            col.markdown(f'<div class="stat finding"><div class="lbl">{head}</div><p>{text}</p></div>', unsafe_allow_html=True)

# ---------- 1. Coverage ----------
with tab_cov:
    st.markdown('<div class="kicker">Question 1</div>', unsafe_allow_html=True)
    st.markdown('<div class="headline">How is coverage spread across collection types, houses and years?</div>', unsafe_allow_html=True)
    sel, shown, label = filters("cov")
    if sel.empty:
        st.info("No reviewed shows match this selection. Choose at least one collection type and a wider year range.")
    else:
        selection_line(sel, label)
        a, b = st.columns(2, gap="large")
        with a:
            st.markdown("### Reviewed shows per year")
            per_year = sel.groupby(["year", "collection_group"]).size().reset_index(name="shows")
            fig = px.line(per_year, x="year", y="shows", color="collection_group", color_discrete_map=COLORS,
                          category_orders={"collection_group": shown},
                          labels={"year": "Season year", "shows": "Reviewed shows", "collection_group": "Collection type"})
            fig.for_each_trace(lambda t: t.update(name=LABELS[t.name], line_width=2,
                                                  hovertemplate="%{x}: %{y} shows<extra>" + LABELS[t.name] + "</extra>"))
            chart_style(fig, 400)
            fig.update_layout(hovermode="x unified")
            show_chart(fig)
            st.markdown("Ready-to-wear is covered the most every year. Menswear arrives around 2005 and pre-collections around 2007, "
                        "so comparisons between types mostly describe the years after that. Dips in menswear (2010) and "
                        "pre-collections (2018) are gaps in the data, and the final year is incomplete.")
        with b:
            st.markdown("### The 15 most-covered houses")
            top = sel["fashion_house"].value_counts().head(15).index
            hc = sel[sel["fashion_house"].isin(top)].groupby(["fashion_house", "collection_group"]).size().reset_index(name="shows")
            fig = px.bar(hc, y="fashion_house", x="shows", color="collection_group", orientation="h", color_discrete_map=COLORS,
                         category_orders={"collection_group": shown, "fashion_house": list(top)},
                         labels={"fashion_house": "", "shows": "Reviewed shows", "collection_group": "Collection type"})
            fig.for_each_trace(lambda t: t.update(name=LABELS[t.name], marker_line_color=PAPER, marker_line_width=1.5))
            chart_style(fig, 480)
            show_chart(fig)
            share = sel["fashion_house"].isin(top).mean() * 100
            st.markdown(f"These 15 houses supply {share:.1f}% of the {len(sel):,} shows in this selection, out of "
                        f"{sel['fashion_house'].nunique()} houses, so coverage is spread widely. Couture, though, comes from only a handful of them.")

# ---------- 2. Review length ----------
with tab_len:
    st.markdown('<div class="kicker">Question 2</div>', unsafe_allow_html=True)
    st.markdown('<div class="headline">How does review length vary across collection types?</div>', unsafe_allow_html=True)
    sel, shown, label = filters("len")
    if sel.empty:
        st.info("No reviewed shows match this selection. Choose at least one collection type and a wider year range.")
    else:
        selection_line(sel, label)
        a, b = st.columns([1.4, 1], gap="large")
        with a:
            cap = sel["review_words"].quantile(0.99)
            counts = sel["collection_group"].value_counts()
            fig = px.box(sel, x="collection_group", y="review_words", color="collection_group", color_discrete_map=COLORS,
                         category_orders={"collection_group": shown}, points=False,
                         labels={"collection_group": "Collection type", "review_words": "Review length (words)"})
            fig.update_xaxes(tickvals=shown, ticktext=[f"{LABELS[t]}<br>n={counts.get(t, 0):,}" for t in shown])
            fig.update_yaxes(range=[0, cap])
            chart_style(fig, 440)
            fig.update_layout(showlegend=False)
            show_chart(fig)
            st.caption(f"Axis cut at {cap:.0f} words (99th percentile of this selection). "
                       f"{(sel['review_words'] > cap).sum()} longer reviews are hidden from view but included in every number.")
        with b:
            st.markdown("### The typical show")
            tbl = sel.groupby("collection_group").agg(
                shows=("review_words", "size"), words=("review_words", "median"), photos=("n_looks", "median")).reindex(shown)
            tbl.index = [LABELS[t] for t in tbl.index]
            tbl.columns = ["Shows", "Median review (words)", "Median photos"]
            st.dataframe(tbl.style.format("{:,.0f}"), width="stretch")
            st.markdown("The line in each box is the typical (median) review; the box holds the middle half. "
                        "Couture and menswear reviews run longest and pre-collections shortest. "
                        "The boxes overlap a lot, so collection type explains only part of how long a review is: "
                        "the critic, the year and the house may matter too.")

# ---------- 3. Themes ----------
with tab_themes:
    st.markdown('<div class="kicker">Question 3</div>', unsafe_allow_html=True)
    st.markdown('<div class="headline">What themes set the collection types apart?</div>', unsafe_allow_html=True)
    a, b = st.columns([1, 1], gap="large")
    with a:
        st.markdown("### Share of reviews mentioning each theme")
        fig = px.imshow(THEME_PCT.rename(columns=LABELS), text_auto=".0f", aspect="auto",
                        color_continuous_scale=[[0, "#FBF8F3"], [1, ACCENT]],
                        labels=dict(x="Collection type", y="Theme", color="% of reviews"))
        chart_style(fig, 470)
        fig.update_xaxes(side="top", showline=False, ticks="")
        fig.update_yaxes(showgrid=False)
        fig.update_traces(hovertemplate="%{y} · %{x}: %{z:.1f}% of reviews<extra></extra>")
        show_chart(fig)
        population(ALL_POP)
    with b:
        st.markdown("### Compare one collection type")
        choice = st.radio("Collection type", ORDER, format_func=lambda c: LABELS[c], horizontal=True, key="t_choice")
        n_choice = int(SUMMARY.loc[choice, "shows"])
        ordered = THEME_PCT.loc[[THEMES[k][0] for k in THEMES]]
        fig = go.Figure()
        fig.add_bar(y=ordered.index, x=ordered[choice], orientation="h", marker_color=COLORS[choice], name=LABELS[choice],
                    text=[f"{v:.0f}%" for v in ordered[choice]], textposition="outside",
                    hovertemplate="%{y}: %{x:.1f}% of " + LABELS[choice] + " reviews<extra></extra>")
        fig.add_scatter(y=ordered.index, x=ordered.drop(columns=[choice]).mean(axis=1), mode="markers",
                        marker=dict(symbol="line-ns", size=22, line=dict(width=3, color=INK)),
                        name="Average of the other three types", hovertemplate="%{y}: %{x:.1f}% (other types)<extra></extra>")
        chart_style(fig, 400)
        fig.update_yaxes(autorange="reversed", gridcolor="rgba(0,0,0,0)")
        fig.update_xaxes(title_text="% of reviews mentioning the theme", range=[0, max(80, ordered.values.max() + 10)])
        show_chart(fig)
        population(f"Bars: all {n_choice:,} reviewed {LABELS[choice].lower()} shows. Black marks: average of the other three types.")

    # The words behind each theme
    st.markdown('<div class="kicker section">The words behind each theme</div>', unsafe_allow_html=True)
    rows = "".join(
        f'<div class="theme-row"><div class="note-head">{name}</div>'
        f'<div>{"".join(f"<span class=chip>{html.escape(w)}</span>" for w in words)}</div></div>'
        for name, words in THEMES.values())
    st.markdown(f'<div style="max-width:56rem;margin:0 auto">{rows}</div>', unsafe_allow_html=True)

    st.markdown("### What the reviews say")
    q = st.columns(3, gap="large")
    quotes = [
        ("Craft in couture", "…many more long, flowy chiffon gowns traced with lines of crystal and sequin embroidery.", "Elie Saab · couture · record 5218"),
        ("Tailoring in menswear", "…a navy pinstripe suit and an elegantly elongated black overcoat…", "Balenciaga · menswear · record 1712"),
        ("Everyday dressing in pre-collections", "…something accessible… to pull in the next generation of customers.", "Gucci · pre-collections · record 6883"),
    ]
    for col, (head, text, cite) in zip(q, quotes):
        col.markdown(f'<div class="kicker">{head}</div><div class="pull">“{html.escape(text)}”</div><div class="cite">{cite}</div>',
                     unsafe_allow_html=True)
   

# ---------- Notes & Limits ----------
with tab_notes:
    st.markdown('<div class="kicker">Notes &amp; limits</div>', unsafe_allow_html=True)
    st.markdown('<div class="headline">How this was made, and what it can’t tell you</div>', unsafe_allow_html=True)

   
    # The data, and what one row is
    st.markdown('<div class="kicker section">The data</div>', unsafe_allow_html=True)
    d1, d2 = st.columns(2, gap="large")
    d1.markdown(
        '<div class="prose"><div class="note-head">Source</div>'
        '<p>I use FashionDB from Hugging Face '
        '(<a href="https://huggingface.co/datasets/traopia/FashionDB" target="_blank">huggingface.co/datasets/traopia/FashionDB</a>), '
        'and the file <code>data_vogue_final.parquet</code>. The dataset’s authors collected it from Vogue Runway’s website, '
        'and their code is on GitHub (<a href="https://github.com/traopia/FashionDB" target="_blank">github.com/traopia/FashionDB</a>). '
        'It has 14,287 shows from 382 fashion houses, from 1988 to 2025.</p></div>', unsafe_allow_html=True)
    d2.markdown(
        '<div class="prose"><div class="note-head">What one row is</div>'
        '<p>One row is one fashion show as covered on Vogue Runway. It can describe the houses in FashionDB that Vogue covered. '
        'It can’t describe all of fashion, or everything Vogue has published.</p></div>', unsafe_allow_html=True)

    # Fields used
    st.markdown('<div class="kicker section">Fields I use</div>', unsafe_allow_html=True)
    fields = [("Numbers", ["year", "review length in words", "number of runway photos"]),
              ("Categories", ["fashion house", "collection type", "season", "reviewer"]),
              ("Free text", ["the written review of each show"])]
    for col, (head, items) in zip(st.columns(3, gap="large"), fields):
        col.markdown(f'<div class="note-step"><div class="note-head">{head}</div>'
                     f'<div style="margin-top:.6rem">{"".join(f"<span class=chip>{w}</span>" for w in items)}</div></div>',
                     unsafe_allow_html=True)

    # Method, as numbered steps
    st.markdown('<div class="kicker section">How this was made</div>', unsafe_allow_html=True)
    steps = [
        ("Collection type", "The category column had couture, ready-to-wear and menswear; only the season column said resort or pre-fall. "
                            "I combined the two into one collection type."),
        ("Cleaning", "I merged resort and pre-fall into <i>pre-collections</i>, "
                     f"and removed 223 bridal and regional shows and 81 unreviewed menswear shows, leaving {N_ALL:,}."),
        ("Themes", "Each theme is a short list of words. A review counts as mentioning a theme if it uses any of them."),
        ("Checking", "I checked the matches by reading a random sample of 40 reviews, 10 per collection type."),
    ]
    for col, (i, (head, text)) in zip(st.columns(4, gap="large"), enumerate(steps, 1)):
        col.markdown(f'<div class="note-step"><div class="n">{i:02d}</div><div class="note-head">{head}</div><p>{text}</p></div>',
                     unsafe_allow_html=True)

    # Limits
    st.markdown('<div class="kicker section">Limitations</div>', unsafe_allow_html=True)
    limits = [
        ("Collection type is split across two columns", "The dataset didn’t have one column saying which kind of collection each show was, "
         "so I had to build it myself. The category column had couture, ready-to-wear and menswear. The season column was the only place "
         "that said resort or pre-fall. For those shows, category was left empty."),
        ("Missing reviews and reviewers", "81 menswear shows have no real review, and 308 shows have no reviewer named."),
        ("Some shows removed", "I removed 223 bridal and regional fashion week shows because they are outside my question."),
        ("Very uneven groups", "There are 7,992 ready-to-wear shows but only 461 couture."),
        ("Not all of fashion", "Only the houses in FashionDB that Vogue covered, not all of fashion or everything Vogue has published."),
        ("Words, not clothes", "A show counted as <i>romantic</i> means the critic used a romantic word, not that the clothes look romantic."),
        ("Keyword matching misses meaning", "One review counted as craft for the word “crafty”, while describing a move away from that look."),
        ("Coverage changes over time", "Coverage falls after 2016 and drops sharply in 2025. The 2025 drop is because the data was collected "
         "partway through the year. The 2018 pre-collections gap appears to be missing data. The decline around 2020 may partly "
         "reflect real changes like the pandemic, but it also reflects that FashionDB follows a fixed list of houses, so newer labels are missing."),
        ("Why reviews differ is unknown", "Length and wording could depend on the critic, the year or the house, not only the collection type."),
        ("Photos are a rough measure", "Photo counts stand in for the number of looks and can include detail shots."),
        ("Copyrighted text", "The reviews are Vogue’s copyrighted writing, so I explain how to load the data from Hugging Face."),
    ]
    items = "".join(f"<li><b>{head}.</b> {text}</li>" for head, text in limits)
    st.markdown(f'<ul class="limits">{items}</ul>', unsafe_allow_html=True)

    st.markdown('<div class="source">Data: FashionDB (traopia/FashionDB) · Reviews © Vogue Runway</div>', unsafe_allow_html=True)
