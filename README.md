# Anime Acquisition Dashboard

**Decision-maker**: Content Acquisition Manager (Anime Vertical), reviewing quarterly.

**Dataset**: `anime-dataset-2026.csv` — one row per anime title, containing Score, Genres, Aired, Status, Studios, Members, Favorites, Scored By, and Episodes.

---

## 1. Dashboard Rationale

The Content Acquisition Manager needs to decide how to allocate the quarterly acquisition budget across different genres, studios, and title statuses. Currently, the manager relies on scattered rankings or manual CSV lookups, which is time-consuming and easily misses high-score titles with moderate member counts that haven't been aggressively acquired yet. This leads to direct opportunity costs during the acquisition window.

The dashboard allows the manager to **switch filters and drill down according to their own judgment path** during each quarterly cycle. A weekly report only presents a fixed slice, and one-off analysis can't be reused next quarter, whereas acquisition decisions are repetitive.

**If the Content Acquisition Manager sees a cluster of high-score anime concentrated in a specific genre with strong member counts on this dashboard, they will allocate a larger portion of the quarterly acquisition budget to that genre and approach the associated studios for licensing deals.**

---

## 2. Metrics and Charts

**Top (Visible in 5 seconds)**
- High-score titles (Score ≥ 8.0)
- Currently Airing count
- Average Score

**Middle (Supporting Charts)**
- High-score titles by genre (Bar chart): Explains which genres concentrate high scores.
- Supply and average score over time (Line chart): Explains how content supply and quality change over time.

**Bottom (Expandable Table)**
- Top 20 titles sorted by score, showing genres, studios, members, and status.

---

## 3. What I Deliberately Left Out

- **Favorites Leaderboard**: Favorites are highly sensitive to individual user behavior and have no stable causal link to acquisition value. A title with high favorites might already be exclusively locked, or the favorites might just be long-term accumulation, not reflecting current value.
- **Rank Field**: A derived metric influenced by both score and number of scorers, highly sensitive to minor data snapshot changes. The manager needs absolute scores and member counts for actionable insight, not a relative position that encourages over-interpreting minor fluctuations.

---

## 4. Data Pitfalls Handled

- **Scores based on very few users**: Some titles' scores come from a tiny number of scorers, lacking representativeness. Supporting charts only include titles with a `Scored By` count above a threshold; the average score is evaluated alongside the median.
- **Inconsistent `Aired` formats**: Ranges like `"Oct 20, 1999 to ?"` cannot be parsed directly. The time trend chart extracts only parseable start years and adds a footnote on the dashboard.
- **"Currently Airing" includes old titles**: E.g., One Piece is currently airing but premiered long ago. The dashboard notes the difference between long-running shows and recent new releases to avoid misinterpreting "airing" as "fresh content."

---

## 5. Models Compared

Features: `Members`, `Scored By`, `Favorites`, `Episodes`; Target: `Score`; Train/Test split 80/20 (`random_state=42`).

| Model | RMSE | MAE | R² |
|---|---|---|---|
| SGD Linear Regression | 0.8197 | 0.6479 | 0.1744 |
| Random Forest | **0.6197** | **0.4546** | **0.5281** |

**Conclusion**: Random Forest outperforms the linear model across all metrics (RMSE lower by ~24%, R² improved from 0.17 to 0.53). This indicates a clear non-linear relationship between the features and the score. For acquisition decisions, this means we cannot estimate a title's score using a simple linear weighting formula; we need a model that captures complex interactions.

---

## 6. LLM Interaction

The bottom of the dashboard features a natural language Q&A section powered by the DeepSeek API (OpenAI-compatible endpoint). It takes the top 10 titles by score from the current filter results as context and asks the LLM to answer user questions based strictly on this data, stating clearly if the data is insufficient. The API credentials are stored in Streamlit secrets and never committed to the repository.

---

## 7. Refresh Frequency

**Production refresh**: Weekly (e.g., Sunday night).
**Review cadence**: Quarterly (concentrated review at the beginning of each quarter).

**Trigger condition**: When the weekly count of titles with Score ≥ 8.0 and Scored By ≥ 10,000 exceeds twice the historical average for two consecutive weeks, the manager is alerted to review the dashboard early and evaluate the need for proactive outreach.

**Cost of stale data**: A one-week delay might cause the team to miss a title that just crossed an 8.0 score and is rapidly gaining members, potentially losing the exclusive rights to a competitor. However, a one-day delay has near-zero cost, as acquisitions are not daily operations.

---

## 8. Links

- **GitHub Repository**: https://github.com/SunYoubei/anime-dashboard
- **Live App**: https://anime-dashboard-5uo4qy5pxhk9cazprhcgaj.streamlit.app/
