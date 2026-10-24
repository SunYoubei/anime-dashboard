# C:\Users\Iris\ml4biz\in-class\app.py
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
from openai import OpenAI

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "anime-dataset-2026.csv"

st.set_page_config(page_title="Anime Acquisition Dashboard", layout="wide")


@st.cache_data
def load_data():
    df = pd.read_csv(CSV_PATH)
    for col in ["Score", "Members", "Scored By", "Favorites", "Episodes"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["Year"] = pd.to_datetime(df["Aired"], errors="coerce").dt.year
    return df


df = load_data()

# ---------- 侧边栏过滤器 ----------
st.sidebar.header("Filters")
all_genres = sorted({g.strip() for genres in df["Genres"].dropna() for g in genres.split(",")})
selected_genres = st.sidebar.multiselect("Genres", all_genres, default=all_genres[:6])

year_min = int(df["Year"].min()) if df["Year"].notna().any() else 1963
year_max = int(df["Year"].max()) if df["Year"].notna().any() else 2006
year_range = st.sidebar.slider("Year range", year_min, year_max, (1990, year_max))

status_options = df["Status"].dropna().unique().tolist()
selected_status = st.sidebar.multiselect("Status", status_options, default=status_options)

mask = (
    df["Genres"].fillna("").apply(lambda x: any(g in x for g in selected_genres))
    & df["Year"].between(year_range[0], year_range[1])
    & df["Status"].isin(selected_status)
)
filtered = df[mask]

# ---------- Top: Headline Metrics ----------
st.title("Anime Acquisition Dashboard")
st.caption("Decision-maker: Content Acquisition Manager · Review cadence: quarterly · Intended refresh: weekly")

c1, c2, c3 = st.columns(3)
c1.metric("High-score titles (Score ≥ 8.0)", f"{(filtered['Score'] >= 8.0).sum():,}")
c2.metric("Currently Airing", f"{(filtered['Status'] == 'Currently Airing').sum():,}")
c3.metric("Average Score", f"{filtered['Score'].mean():.2f}" if len(filtered) else "—")

# ---------- Middle: Supporting Charts ----------
st.subheader("High-score titles by genre")
high = filtered[filtered["Score"] >= 8.0].copy()
if len(high):
    high["Genre"] = high["Genres"].str.split(",")
    exploded = high.explode("Genre")
    exploded["Genre"] = exploded["Genre"].str.strip()
    genre_counts = exploded["Genre"].value_counts().head(12).reset_index()
    genre_counts.columns = ["Genre", "Count"]
    st.plotly_chart(px.bar(genre_counts, x="Count", y="Genre", orientation="h"), use_container_width=True)
else:
    st.info("No high-score titles under current filters.")

st.subheader("Supply and average score over time")
yearly = (
    filtered.dropna(subset=["Year"])
    .groupby("Year")
    .agg(Titles=("Score", "size"), AvgScore=("Score", "mean"))
    .reset_index()
)
if len(yearly):
    st.plotly_chart(px.line(yearly, x="Year", y=["Titles", "AvgScore"]), use_container_width=True)

# ---------- Bottom: 明细表（可选展开） ----------
with st.expander("Top titles (sorted by score)"):
    cols = ["Name", "Score", "Genres", "Studios", "Members", "Status", "Year"]
    available = [c for c in cols if c in filtered.columns]
    st.dataframe(filtered.nlargest(20, "Score")[available].reset_index(drop=True), use_container_width=True)

# ---------- LLM 自然语言查询区 ----------
st.divider()
st.subheader("Ask the data (LLM-powered)")

if "LLM_API_KEY" in st.secrets:
    client = OpenAI(
        base_url=st.secrets.get("LLM_BASE_URL", "https://api.openai.com/v1"),
        api_key=st.secrets["LLM_API_KEY"],
    )

    question = st.text_input(
        "用自然语言提问",
        placeholder="例如：评分最高的前 5 部动漫是哪些？",
    )

    if st.button("Ask") and question:
        sample = (
            filtered.nlargest(10, "Score")[["Name", "Score", "Genres", "Members", "Status"]]
            .to_csv(index=False)
        )
        prompt = f"""You are a data analyst for an anime acquisition team.
The current filtered dataset has {len(filtered)} titles.
Top 10 titles by score:
{sample}

Answer the user's question using only the data above. If data is insufficient, say so.
User question: {question}"""
        with st.spinner("Thinking..."):
            resp = client.chat.completions.create(
                model=st.secrets.get("LLM_MODEL", "gpt-4o-mini"),
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
            )
        st.write(resp.choices[0].message.content)
else:
    st.info("LLM not configured. Add LLM_API_KEY to Streamlit secrets to enable Q&A.")