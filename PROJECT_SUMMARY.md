# MLB 9th Hitter Analysis – Project Summary

**A complete data pipeline analyzing whether the 9th hitter in a baseball lineup actually matters.**

> **Key finding**: A 0.100 increase in 9th‑hitter OPS correlates with ~0.15 additional runs per game – that's about 24 runs per season, or 2–3 wins.

---

## 📌 Project Overview

| Item | Details |
|------|---------|
| **Goal** | Determine if the 9th hitter has a measurable impact on team scoring |
| **Approach** | End‑to‑end data pipeline: API → SQLite → Analysis → Dashboard |
| **Data** | MLB game data from 2020–2026 (350,000+ rows, 15,000+ games) |
| **Outcome** | Interactive dashboard and regression analysis showing a significant but modest effect |

---

## 🛠️ Technical Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              DATA PIPELINE                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌───────────┐ │
│  │  MLB Stats   │───▶│   Python     │───▶│   SQLite     │───▶│ Analysis  │ │
│  │     API      │    │  Collection  │    │   Database   │    │           │ │
│  └──────────────┘    └──────────────┘    └──────────────┘    └───────────┘ │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                         VISUALIZATION LAYER                           │ │
│  ├───────────────────────────────────────────────────────────────────────┤ │
│  │  Streamlit Dashboard │ Tableau Public │ Matplotlib │ Jupyter Notebook │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

| Layer | Tools |
|-------|-------|
| **Data Collection** | Python, `MLB-StatsAPI`, requests |
| **Storage** | SQLite (6 tables: games, players, teams, box_scores_batting, box_scores_pitching, play_by_play) |
| **Data Processing** | Pandas, NumPy, SQL (CTEs, window functions) |
| **Analysis** | scikit‑learn (linear regression) |
| **Visualization** | Streamlit, Matplotlib, Seaborn, Tableau Public |
| **AI Assistance** | GitHub Copilot, Claude, ChatGPT |

---

## 📊 Key Metrics & Calculations

| Metric | Formula | Source |
|--------|---------|--------|
| **OPS** | OBP + SLG | Calculated from counting stats |
| **wOBA** | Weighted On‑Base Average | Calculated from counting stats |
| **OBP** | (H + BB + HBP) / (AB + BB + HBP + SF) | Counting stats |
| **SLG** | (H + 2B + 2×3B + 3×HR) / AB | Counting stats |
| **Runs/Game** | (Home_Score + Away_Score) / Games | Game data |

### wOBA Weights Used

| Event | Weight |
|-------|--------|
| Walk / HBP | 0.69 |
| Single | 0.89 |
| Double | 1.27 |
| Triple | 1.62 |
| Home Run | 2.10 |

---

## 📈 Key Findings

### 1. Best Single‑Season 9th Hitter Performance

The **2022 New York Yankees** had the best 9th‑hitter production in the dataset with a **.977 OPS** – significantly above the league average of ~.700.

### 2. League Average 9th Hitter OPS Over Time

| Season | Average OPS |
|--------|-------------|
| 2020 | .675 |
| 2021 | .710 |
| 2022 | .715 |
| 2023 | .710 |
| 2024 | .710 |
| 2025 | .695 |
| 2026 | .710 |

### 3. Regression Analysis

| Metric | Coefficient for 9th | R² | Interpretation |
|--------|---------------------|-----|----------------|
| **OPS** | 1.50 | 0.65 | A 0.100 increase → +0.15 runs/game |
| **wOBA** | 1.45 | 0.63 | A 0.100 increase → +0.145 runs/game |

**Interpretation**: A 0.100 increase in 9th‑hitter OPS adds ~0.15 runs per game (24 runs/season), controlling for rest‑of‑lineup quality.

### 4. 9th Hitter vs. Rest of Lineup

On average, the 9th hitter underperforms the rest of the lineup by **~0.040 OPS points**.

### 5. 9th Hitter Impact on Scoring

| 9th Hitter Status | Games | Avg Runs/Game | High Scoring % |
|-------------------|-------|---------------|----------------|
| Reached Base | 8,200 | 4.8 | 58% |
| No Reach | 6,800 | 4.5 | 52% |
| No 9th Hitter | 200 | 4.2 | 48% |

---

## 🧠 Challenges & Solutions

| Challenge | Solution |
|-----------|----------|
| **API Rate Limiting** | Implemented delays and retry logic |
| **Player ID Mismatch** | Matched by name and position |
| **Backfilling Batting Order** | Processed 15,000+ games to populate positions 1‑9 |
| **Missing Rate Stats** | Calculated OPS and wOBA from counting stats |
| **Large Database File** | Added to .gitignore; users can regenerate with `collect_mlb_data.py` |
| **Data Quality Validation** | Verified box score consistency and unique player IDs |

---

## 🎯 Skills Demonstrated

| Skill | How It's Shown |
|-------|----------------|
| **Data Engineering** | Automated pipeline fetching from MLB Stats API |
| **Database Design** | Normalized SQLite schema with 6 tables |
| **SQL** | Complex queries: CTEs, window functions, aggregations |
| **API Integration** | HTTP requests, rate limiting, error handling |
| **Data Analysis** | Pandas, regression analysis, feature engineering |
| **Visualization** | Streamlit dashboard, Matplotlib, Tableau Public |
| **Problem Solving** | ID mismatches, missing data, backfilling |
| **Version Control** | Git, GitHub with clean commit history |
| **AI Collaboration** | Used AI tools for development and documentation |

---

## 📂 Code Structure
MLB-Stats-Collection-and-Spray-Charts/
├── README.md # Full project documentation
├── PROJECT_SUMMARY.md # This file
├── requirements.txt # Python dependencies
├── schema.sql # Database schema
├── LICENSE # MIT License
├── .gitignore # Git ignore rules
├── data/ # Database, CSVs, visualizations
├── scripts/ # All Python scripts
│ ├── collect_mlb_data.py # API data ingestion
│ ├── backfill_all.py # Populate batting_order
│ ├── dashboard.py # Streamlit dashboard
│ ├── visualize_9th_hitters.py # Static charts
│ └── export_for_powerbi.py # CSV export for Tableau
├── notebooks/ # Jupyter notebook (AI‑assisted)
└── docs/ # Documentation files

---

## 📊 Dashboard Features

The Streamlit dashboard includes 7 interactive tabs:

| Tab | Feature |
|-----|---------|
| **Team Rankings** | Top teams by 9th hitter OPS with bar chart |
| **Trends** | League average and team‑specific over time |
| **Player Rankings** | Most frequent 9th hitters (by player_id) |
| **9th Hitter Impact** | Runs scored when 9th hitter reaches base vs. not |
| **Lineup Comparison** | OPS by batting order position (1‑9) |
| **Impact Analysis** | Regression with OPS/wOBA + what‑if tool |
| **Data Table** | Filterable data with CSV download |

---

## 🔮 Future Work

- [ ] Add spray‑chart visualizations from play‑by‑play data
- [ ] Incorporate Statcast metrics (exit velocity, launch angle)
- [ ] Build a predictive model for 9th‑hitter performance
- [ ] Real‑time updates during the MLB season
- [ ] Add more advanced metrics (wRC+, xwOBA)
- [ ] Deploy dashboard to Streamlit Cloud
- [ ] Mobile‑optimized dashboard

---

## 📚 References

- [MLB Stats API Documentation](https://statsapi.mlb.com/)
- [FanGraphs wOBA Explanation](https://library.fangraphs.com/offense/woba/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [scikit‑learn Documentation](https://scikit-learn.org/)

---

## 📬 Contact

**Jack Holroyd**  
[GitHub](https://github.com/Jholroyd1)  
[LinkedIn](https://linkedin.com/in/your-linkedin)

---

**Built by Jack Holroyd**