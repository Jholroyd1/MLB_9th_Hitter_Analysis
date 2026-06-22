# ⚾ MLB 9th Hitter Analysis

**An end‑to‑end data pipeline that analyzes the impact of the 9th hitter on MLB team performance (2020–2026).**

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-ff4b4b)](https://streamlit.io/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003b57)](https://www.sqlite.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![AI Assisted](https://img.shields.io/badge/AI-Assisted-blueviolet)](https://github.com/Jholroyd1/MLB-Stats-Collection-and-Spray-Charts)

---

## 📌 Overview

This project answers a simple question: **Does the 9th hitter in a baseball lineup actually matter?**

I built a complete data pipeline that:

- ✅ Fetches MLB game data from the official **MLB Stats API**
- ✅ Stores it in a **SQLite** database (350,000+ rows)
- ✅ Backfills batting order positions (1‑9) for 15,000+ games
- ✅ Calculates advanced metrics (OPS, wOBA)
- ✅ Runs regression analysis to quantify the impact of the 9th hitter
- ✅ Visualizes results with an interactive **Streamlit dashboard** and static charts

### 🔑 Key Finding

> **A 0.100 increase in 9th‑hitter OPS correlates with ~0.15 additional runs per game – that's about 24 runs per season, or 2–3 wins.**

### 🤖 AI Tools & Assistance

This project was developed with the assistance of AI tools to accelerate development and improve code quality:

| Tool | Purpose |
|------|---------|
| **GitHub Copilot** | Code completion, boilerplate generation, and refactoring |
| **Claude / ChatGPT** | Debugging assistance, SQL query optimization, and documentation writing |
| **AI Code Review** | Automated suggestions for code quality and best practices |

All AI‑generated code and content has been **reviewed, tested, and validated** by the author to ensure correctness, reliability, and alignment with project goals. The architecture, data modeling, analysis methodology, and key insights are the result of human‑led decision‑making.

---

## 🛠️ Tech Stack

| Layer | Tools |
|-------|-------|
| **Data Collection** | Python, `MLB-StatsAPI`, `requests` |
| **Storage** | SQLite, SQL |
| **Data Processing** | Pandas, NumPy |
| **Analysis** | scikit‑learn (linear regression) |
| **Visualization** | Matplotlib, Seaborn, Streamlit, Tableau Public |
| **Version Control** | Git, GitHub |
| **AI Assistance** | GitHub Copilot, Claude, ChatGPT |

---

## 📊 Dashboard

### Streamlit Dashboard (Interactive)

Run the dashboard locally to explore the data:

```bash
streamlit run scripts/dashboard.py
```

The dashboard includes:

| Tab | Feature |
|-----|---------|
| **Team Rankings** | Top teams by 9th hitter OPS |
| **Trends** | League average and team‑specific over time |
| **Player Rankings** | Most frequent 9th hitters |
| **9th Hitter Impact** | Games where 9th hitter reaches base vs. not |
| **Lineup Comparison** | OPS by batting order position (1-9) |
| **Impact Analysis** | Regression using OPS and wOBA with what‑if tool |
| **Data Table** | Raw data with CSV download |

### Tableau Public

Download `data/master_9th_hitter_data.csv` and import into [Tableau Public](https://public.tableau.com/) for additional visualization options.

### Static Visualizations

The `data/visualizations/` folder contains static charts:

- `2026_top_10.png` – Top teams in 2026
- `season_avg_trend.png` – League average over time
- `2022_comparison.png` – 2022 season comparison (Yankees highlighted)

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/Jholroyd1/MLB-Stats-Collection-and-Spray-Charts.git
cd MLB-Stats-Collection-and-Spray-Charts
```

### 2. Set Up Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Initialize the Database

```bash
python3 scripts/init_database.py
```

### 5. Collect Data (Optional)

To collect fresh data from the MLB API:

```bash
python3 scripts/collect_mlb_data.py --season 2024
```

### 6. Run the Dashboard

```bash
streamlit run scripts/dashboard.py
```

---

## 📂 Project Structure

```
MLB-Stats-Collection-and-Spray-Charts/
├── data/                         # Database and exported CSV files
│   ├── mlb_data.db               # SQLite database
│   ├── master_9th_hitter_data.csv  # Master CSV for Tableau
│   └── visualizations/           # Static charts
├── scripts/                      # All Python scripts
│   ├── collect_mlb_data.py       # Data ingestion from MLB API
│   ├── backfill_all.py           # Populate batting_order column
│   ├── dashboard.py              # Streamlit dashboard
│   ├── visualize_9th_hitters.py  # Generate static visualizations
│   └── export_for_powerbi.py     # CSV export for Tableau
├── notebooks/                    # Jupyter notebooks
│   └── MLB_Player_Data_Analysis.ipynb  # (AI-assisted)
├── docs/                         # Documentation files
│   ├── COLLECTION_STATUS.md
│   ├── MULTI_SEASON_STATUS.md
│   └── QUICK_REFERENCE.md
├── examples/                     # Sample outputs and charts
├── requirements.txt              # Python dependencies
├── schema.sql                    # Database schema
├── LICENSE                       # MIT License
└── README.md                     # This file
```

---

## 🔍 Analysis & Key Findings

### 1. Best Single-Season 9th Hitter Performance

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

Using **OPS** and **wOBA** as predictors, I ran a linear regression to estimate the impact of the 9th hitter on team runs per game:

| Metric | Coefficient for 9th | R² |
|--------|---------------------|-----|
| **OPS** | 1.50 | 0.65 |
| **wOBA** | 1.45 | 0.63 |

**Interpretation**: A 0.100 increase in 9th‑hitter OPS adds ~0.15 runs per game (24 runs/season), controlling for rest‑of‑lineup quality.

### 4. 9th Hitter vs. Rest of Lineup

On average, the 9th hitter underperforms the rest of the lineup by **~0.040 OPS points**, consistent with the traditional view of the 9th spot as the weakest hitter.

### 5. 9th Hitter Impact on Scoring

| 9th Hitter Status | Games | Avg Runs/Game | High Scoring % |
|-------------------|-------|---------------|----------------|
| Reached Base | 8,200 | 4.8 | 58% |
| No Reach | 6,800 | 4.5 | 52% |
| No 9th Hitter | 200 | 4.2 | 48% |

---

## 🧠 Challenges Overcome

### 1. API Rate Limiting
Implemented delays and retry logic to stay within the MLB Stats API's rate limits.

### 2. Player ID Mismatch
The API uses **person IDs** (e.g., 116706) while the database uses **MLBAM IDs** (e.g., 435062). Solved by matching players by name and position.

### 3. Backfilling Batting Order
Processed **15,000+ games** to populate the `batting_order` column for all starting players.

### 4. Missing Rate Stats
The raw API data didn't include pre‑calculated OPS, so I calculated it from counting stats (hits, walks, doubles, triples, home runs, at‑bats, etc.).

### 5. Data Quality
Validated that every game has consistent box score totals and that player IDs are unique.

---

## 📈 Future Work

- [ ] Add spray‑chart visualizations from play‑by‑play data
- [ ] Incorporate Statcast metrics (exit velocity, launch angle)
- [ ] Build a predictive model for 9th‑hitter performance
- [ ] Real‑time updates during the MLB season
- [ ] Add more advanced metrics (wRC+, xwOBA)
- [ ] Create a mobile‑optimized version of the dashboard

---

## 📄 License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request.

---

## 📬 Contact

**Jack Holroyd**  
[GitHub](https://github.com/Jholroyd1) | [LinkedIn](https://linkedin.com/in/your-linkedin)

---

## 🙏 Acknowledgments

- Data provided by the [MLB Stats API](https://statsapi.mlb.com/)
- Built with [Streamlit](https://streamlit.io/) for the interactive dashboard
- Inspired by the endless debate over lineup construction in baseball
- AI tools (GitHub Copilot, Claude, ChatGPT) assisted with code generation, debugging, and documentation

---

## 📊 Sample Visualizations

> *The dashboard includes interactive versions of these charts.*

### Top Teams by 9th Hitter OPS (2026)

![2026 Top 10](data/visualizations/2026_top_10.png)

### League Average 9th Hitter OPS Over Time

![Season Trend](data/visualizations/season_avg_trend.png)

### 2022 Season Comparison

![2022 Comparison](data/visualizations/2022_comparison.png)

---

## ⚡ Quick Command Reference

| Task | Command |
|------|---------|
| Collect data | `python scripts/collect_mlb_data.py --season 2024` |
| Backfill batting order | `python scripts/backfill_all.py` |
| Run dashboard | `streamlit run scripts/dashboard.py` |
| Generate static charts | `python scripts/visualize_9th_hitters.py` |
| Export CSV for Tableau | `python scripts/export_for_powerbi.py` |
| Run Jupyter notebook | `jupyter notebook notebooks/MLB_Player_Data_Analysis.ipynb` |

---

**Built by [Jack Holroyd](https://github.com/Jholroyd1)**