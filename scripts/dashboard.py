import sqlite3
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np
from sklearn.linear_model import LinearRegression

# Page config
st.set_page_config(page_title="MLB 9th Hitter Dashboard", layout="wide")
st.title("⚾ MLB 9th Hitter Analysis Dashboard")
st.caption("Explore 9th hitter performance across 2020-2026")

# Database path (from project root)
DB_PATH = 'data/mlb_data.db'

# -------------------- Cached Data Loaders --------------------
@st.cache_data
def load_team_data():
    """Load team-level 9th hitter stats"""
    conn = sqlite3.connect(DB_PATH)
    query = """
    SELECT 
        t.team_name,
        g.season,
        COUNT(*) as games_batting_ninth,
        ROUND(SUM(bb.hits) * 1.0 / NULLIF(SUM(bb.at_bats), 0), 3) as avg_avg,
        ROUND((SUM(bb.hits) + SUM(bb.walks) + SUM(bb.hit_by_pitch)) * 1.0 / 
              NULLIF(SUM(bb.at_bats) + SUM(bb.walks) + SUM(bb.hit_by_pitch) + SUM(bb.sacrifice_flies), 0), 3) as avg_obp,
        ROUND((SUM(bb.hits) + SUM(bb.doubles) + 2*SUM(bb.triples) + 3*SUM(bb.home_runs)) * 1.0 / 
              NULLIF(SUM(bb.at_bats), 0), 3) as avg_slg,
        ROUND(
            ((SUM(bb.hits) + SUM(bb.walks) + SUM(bb.hit_by_pitch)) * 1.0 / 
             NULLIF(SUM(bb.at_bats) + SUM(bb.walks) + SUM(bb.hit_by_pitch) + SUM(bb.sacrifice_flies), 0)) +
            ((SUM(bb.hits) + SUM(bb.doubles) + 2*SUM(bb.triples) + 3*SUM(bb.home_runs)) * 1.0 / 
             NULLIF(SUM(bb.at_bats), 0)), 
        3) as avg_ops,
        ROUND(SUM(bb.rbi), 0) as total_rbi,
        ROUND(SUM(bb.runs), 0) as total_runs
    FROM box_scores_batting bb
    JOIN games g ON bb.game_id = g.game_id
    LEFT JOIN teams t ON bb.team_id = t.team_id
    WHERE bb.batting_order = 9
      AND bb.batting_order IS NOT NULL
      AND bb.at_bats > 0
    GROUP BY t.team_name, g.season
    HAVING games_batting_ninth >= 30
    ORDER BY g.season DESC, avg_ops DESC;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

@st.cache_data
def load_player_data():
    """Load player-level 9th hitter stats (by player_id)"""
    conn = sqlite3.connect(DB_PATH)
    query = """
    SELECT 
        bb.player_id,
        t.team_name,
        g.season,
        COUNT(*) as games_batting_ninth,
        ROUND(SUM(bb.hits) * 1.0 / NULLIF(SUM(bb.at_bats), 0), 3) as avg_avg,
        ROUND((SUM(bb.hits) + SUM(bb.walks) + SUM(bb.hit_by_pitch)) * 1.0 / 
              NULLIF(SUM(bb.at_bats) + SUM(bb.walks) + SUM(bb.hit_by_pitch) + SUM(bb.sacrifice_flies), 0), 3) as avg_obp,
        ROUND((SUM(bb.hits) + SUM(bb.doubles) + 2*SUM(bb.triples) + 3*SUM(bb.home_runs)) * 1.0 / 
              NULLIF(SUM(bb.at_bats), 0), 3) as avg_slg,
        ROUND(
            ((SUM(bb.hits) + SUM(bb.walks) + SUM(bb.hit_by_pitch)) * 1.0 / 
             NULLIF(SUM(bb.at_bats) + SUM(bb.walks) + SUM(bb.hit_by_pitch) + SUM(bb.sacrifice_flies), 0)) +
            ((SUM(bb.hits) + SUM(bb.doubles) + 2*SUM(bb.triples) + 3*SUM(bb.home_runs)) * 1.0 / 
             NULLIF(SUM(bb.at_bats), 0)), 
        3) as avg_ops,
        ROUND(SUM(bb.rbi), 0) as total_rbi,
        ROUND(SUM(bb.runs), 0) as total_runs
    FROM box_scores_batting bb
    JOIN games g ON bb.game_id = g.game_id
    LEFT JOIN teams t ON bb.team_id = t.team_id
    WHERE bb.batting_order = 9
      AND bb.batting_order IS NOT NULL
      AND bb.at_bats > 0
    GROUP BY bb.player_id, t.team_name, g.season
    HAVING games_batting_ninth >= 20
    ORDER BY games_batting_ninth DESC;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

@st.cache_data
def load_impact_data():
    """Load game-level data for 9th hitter impact analysis"""
    conn = sqlite3.connect(DB_PATH)
    query = """
    WITH ninth_hitter_games AS (
        SELECT 
            game_id,
            CASE 
                WHEN MAX(CASE WHEN batting_order = 9 AND (hits > 0 OR walks > 0 OR hit_by_pitch > 0) THEN 1 ELSE 0 END) = 1 
                THEN 'Reached Base'
                WHEN MAX(CASE WHEN batting_order = 9 THEN 1 ELSE 0 END) = 1 
                THEN 'No Reach'
                ELSE 'No 9th Hitter'
            END as ninth_hitter_status
        FROM box_scores_batting
        WHERE game_id IN (SELECT game_id FROM games)
        GROUP BY game_id
    )
    SELECT 
        nhg.ninth_hitter_status,
        COUNT(*) as games,
        ROUND(AVG(g.home_score + g.away_score), 1) as avg_total_runs,
        ROUND(100.0 * SUM(CASE WHEN (g.home_score + g.away_score) >= 5 THEN 1 ELSE 0 END) / COUNT(*), 1) as pct_high_scoring,
        ROUND(100.0 * SUM(CASE WHEN g.home_score > g.away_score THEN 1 ELSE 0 END) / COUNT(*), 1) as home_win_pct,
        ROUND(100.0 * SUM(CASE WHEN g.away_score > g.home_score THEN 1 ELSE 0 END) / COUNT(*), 1) as away_win_pct,
        ROUND(AVG(g.home_score), 1) as avg_home_runs,
        ROUND(AVG(g.away_score), 1) as avg_away_runs
    FROM ninth_hitter_games nhg
    JOIN games g ON nhg.game_id = g.game_id
    GROUP BY nhg.ninth_hitter_status
    ORDER BY avg_total_runs DESC;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

@st.cache_data
def load_lineup_comparison(season=None, team=None):
    """Load OPS by batting order position for a given season and team"""
    conn = sqlite3.connect(DB_PATH)
    query = """
    SELECT 
        g.season,
        t.team_name,
        bb.batting_order,
        COUNT(*) as plate_appearances,
        ROUND(SUM(bb.hits) * 1.0 / NULLIF(SUM(bb.at_bats), 0), 3) as avg_avg,
        ROUND((SUM(bb.hits) + SUM(bb.walks) + SUM(bb.hit_by_pitch)) * 1.0 / 
              NULLIF(SUM(bb.at_bats) + SUM(bb.walks) + SUM(bb.hit_by_pitch) + SUM(bb.sacrifice_flies), 0), 3) as avg_obp,
        ROUND((SUM(bb.hits) + SUM(bb.doubles) + 2*SUM(bb.triples) + 3*SUM(bb.home_runs)) * 1.0 / 
              NULLIF(SUM(bb.at_bats), 0), 3) as avg_slg,
        ROUND(
            ((SUM(bb.hits) + SUM(bb.walks) + SUM(bb.hit_by_pitch)) * 1.0 / 
             NULLIF(SUM(bb.at_bats) + SUM(bb.walks) + SUM(bb.hit_by_pitch) + SUM(bb.sacrifice_flies), 0)) +
            ((SUM(bb.hits) + SUM(bb.doubles) + 2*SUM(bb.triples) + 3*SUM(bb.home_runs)) * 1.0 / 
             NULLIF(SUM(bb.at_bats), 0)), 
        3) as avg_ops
    FROM box_scores_batting bb
    JOIN games g ON bb.game_id = g.game_id
    LEFT JOIN teams t ON bb.team_id = t.team_id
    WHERE bb.batting_order IS NOT NULL
      AND bb.batting_order BETWEEN 1 AND 9
      AND bb.at_bats > 0
    """
    if season is not None:
        query += f" AND g.season = {season}"
    if team is not None and team != "All":
        query += f" AND t.team_name = '{team}'"
    query += """
    GROUP BY g.season, t.team_name, bb.batting_order
    ORDER BY g.season, t.team_name, bb.batting_order;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

@st.cache_data
def load_impact_analysis():
    """Load team-season data with OPS and wOBA for 9th hitter and rest of lineup."""
    conn = sqlite3.connect(DB_PATH)
    query = """
    WITH team_season_stats AS (
        SELECT 
            g.season,
            t.team_name,
            -- 9th hitter OPS
            ROUND(
                ((SUM(CASE WHEN bb.batting_order = 9 THEN bb.hits END) + SUM(CASE WHEN bb.batting_order = 9 THEN bb.walks END) + SUM(CASE WHEN bb.batting_order = 9 THEN bb.hit_by_pitch END)) * 1.0 / 
                 NULLIF(SUM(CASE WHEN bb.batting_order = 9 THEN bb.at_bats END) + SUM(CASE WHEN bb.batting_order = 9 THEN bb.walks END) + SUM(CASE WHEN bb.batting_order = 9 THEN bb.hit_by_pitch END) + SUM(CASE WHEN bb.batting_order = 9 THEN bb.sacrifice_flies END), 0)) +
                ((SUM(CASE WHEN bb.batting_order = 9 THEN bb.hits END) + SUM(CASE WHEN bb.batting_order = 9 THEN bb.doubles END) + 2*SUM(CASE WHEN bb.batting_order = 9 THEN bb.triples END) + 3*SUM(CASE WHEN bb.batting_order = 9 THEN bb.home_runs END)) * 1.0 / 
                 NULLIF(SUM(CASE WHEN bb.batting_order = 9 THEN bb.at_bats END), 0)), 
            3) as ops_9,
            -- Rest of lineup (1-8) OPS
            ROUND(
                ((SUM(CASE WHEN bb.batting_order BETWEEN 1 AND 8 THEN bb.hits END) + SUM(CASE WHEN bb.batting_order BETWEEN 1 AND 8 THEN bb.walks END) + SUM(CASE WHEN bb.batting_order BETWEEN 1 AND 8 THEN bb.hit_by_pitch END)) * 1.0 / 
                 NULLIF(SUM(CASE WHEN bb.batting_order BETWEEN 1 AND 8 THEN bb.at_bats END) + SUM(CASE WHEN bb.batting_order BETWEEN 1 AND 8 THEN bb.walks END) + SUM(CASE WHEN bb.batting_order BETWEEN 1 AND 8 THEN bb.hit_by_pitch END) + SUM(CASE WHEN bb.batting_order BETWEEN 1 AND 8 THEN bb.sacrifice_flies END), 0)) +
                ((SUM(CASE WHEN bb.batting_order BETWEEN 1 AND 8 THEN bb.hits END) + SUM(CASE WHEN bb.batting_order BETWEEN 1 AND 8 THEN bb.doubles END) + 2*SUM(CASE WHEN bb.batting_order BETWEEN 1 AND 8 THEN bb.triples END) + 3*SUM(CASE WHEN bb.batting_order BETWEEN 1 AND 8 THEN bb.home_runs END)) * 1.0 / 
                 NULLIF(SUM(CASE WHEN bb.batting_order BETWEEN 1 AND 8 THEN bb.at_bats END), 0)), 
            3) as ops_1_8,
            -- 9th hitter wOBA
            ROUND(
                (0.69 * (SUM(CASE WHEN bb.batting_order = 9 THEN bb.walks END) + SUM(CASE WHEN bb.batting_order = 9 THEN bb.hit_by_pitch END)) +
                 0.89 * SUM(CASE WHEN bb.batting_order = 9 THEN (bb.hits - bb.doubles - bb.triples - bb.home_runs) END) +
                 1.27 * SUM(CASE WHEN bb.batting_order = 9 THEN bb.doubles END) +
                 1.62 * SUM(CASE WHEN bb.batting_order = 9 THEN bb.triples END) +
                 2.10 * SUM(CASE WHEN bb.batting_order = 9 THEN bb.home_runs END)) * 1.0 /
                NULLIF(SUM(CASE WHEN bb.batting_order = 9 THEN bb.at_bats END) + SUM(CASE WHEN bb.batting_order = 9 THEN bb.walks END) + SUM(CASE WHEN bb.batting_order = 9 THEN bb.hit_by_pitch END) + SUM(CASE WHEN bb.batting_order = 9 THEN bb.sacrifice_flies END), 0),
            3) as wOBA_9,
            -- Rest of lineup (1-8) wOBA
            ROUND(
                (0.69 * (SUM(CASE WHEN bb.batting_order BETWEEN 1 AND 8 THEN bb.walks END) + SUM(CASE WHEN bb.batting_order BETWEEN 1 AND 8 THEN bb.hit_by_pitch END)) +
                 0.89 * SUM(CASE WHEN bb.batting_order BETWEEN 1 AND 8 THEN (bb.hits - bb.doubles - bb.triples - bb.home_runs) END) +
                 1.27 * SUM(CASE WHEN bb.batting_order BETWEEN 1 AND 8 THEN bb.doubles END) +
                 1.62 * SUM(CASE WHEN bb.batting_order BETWEEN 1 AND 8 THEN bb.triples END) +
                 2.10 * SUM(CASE WHEN bb.batting_order BETWEEN 1 AND 8 THEN bb.home_runs END)) * 1.0 /
                NULLIF(SUM(CASE WHEN bb.batting_order BETWEEN 1 AND 8 THEN bb.at_bats END) + SUM(CASE WHEN bb.batting_order BETWEEN 1 AND 8 THEN bb.walks END) + SUM(CASE WHEN bb.batting_order BETWEEN 1 AND 8 THEN bb.hit_by_pitch END) + SUM(CASE WHEN bb.batting_order BETWEEN 1 AND 8 THEN bb.sacrifice_flies END), 0),
            3) as wOBA_1_8,
            -- Runs per game
            ROUND(AVG(g.home_score + g.away_score), 2) as runs_per_game,
            COUNT(DISTINCT g.game_id) as games_played
        FROM box_scores_batting bb
        JOIN games g ON bb.game_id = g.game_id
        LEFT JOIN teams t ON bb.team_id = t.team_id
        WHERE bb.batting_order IS NOT NULL
          AND bb.batting_order BETWEEN 1 AND 9
          AND bb.at_bats > 0
        GROUP BY g.season, t.team_name
    )
    SELECT *
    FROM team_season_stats
    WHERE ops_9 IS NOT NULL AND ops_1_8 IS NOT NULL AND games_played >= 30
    ORDER BY season, team_name;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# -------------------- Load Data --------------------
with st.spinner("Loading data..."):
    team_df = load_team_data()
    player_df = load_player_data()
    impact_df = load_impact_data()
    impact_analysis_df = load_impact_analysis()

st.success(f"Loaded {len(team_df)} team-season records, {len(player_df)} player-season records, {len(impact_analysis_df)} team-season analysis records")

# -------------------- Sidebar Filters --------------------
st.sidebar.header("Filters")
seasons = sorted(team_df['season'].unique(), reverse=True)
selected_season = st.sidebar.selectbox("Select Season", ["All"] + [str(s) for s in seasons])
teams = sorted(team_df['team_name'].unique())
selected_team = st.sidebar.selectbox("Select Team", ["All"] + [str(t) for t in teams])

# Apply filters for team data
filtered_team_df = team_df.copy()
if selected_season != "All":
    filtered_team_df = filtered_team_df[filtered_team_df['season'] == int(selected_season)]
if selected_team != "All":
    filtered_team_df = filtered_team_df[filtered_team_df['team_name'] == selected_team]

# -------------------- Tabs --------------------
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📊 Team Rankings",
    "📈 Trends",
    "🏆 Player Rankings",
    "💥 9th Hitter Impact",
    "🔍 Lineup Comparison",
    "📊 Impact Analysis",
    "📋 Data Table"
])

# ----- Tab 1: Team Rankings -----
with tab1:
    st.header("Team Rankings")
    col1, col2 = st.columns([2, 1])
    with col1:
        fig, ax = plt.subplots(figsize=(12, 8))
        display_df = filtered_team_df.sort_values('avg_ops', ascending=False).head(15)
        bars = ax.bar(display_df['team_name'], display_df['avg_ops'], color='steelblue', edgecolor='black')
        ax.axhline(y=display_df['avg_ops'].mean(), color='red', linestyle='--', alpha=0.7,
                   label=f"Avg: {display_df['avg_ops'].mean():.3f}")
        ax.set_xlabel('Team')
        ax.set_ylabel('OPS')
        ax.set_title(f'Top 15 Teams by 9th Hitter OPS')
        ax.legend()
        plt.xticks(rotation=45, ha='right')
        st.pyplot(fig)
    with col2:
        st.metric("Average OPS", f"{filtered_team_df['avg_ops'].mean():.3f}")
        st.metric("Best OPS", f"{filtered_team_df['avg_ops'].max():.3f}")
        st.metric("Worst OPS", f"{filtered_team_df['avg_ops'].min():.3f}")
        st.metric("Teams", len(filtered_team_df))

# ----- Tab 2: Trends -----
with tab2:
    st.header("Trends Over Time")
    col1, col2 = st.columns(2)
    with col1:
        fig, ax = plt.subplots(figsize=(10, 6))
        season_avg = team_df.groupby('season')['avg_ops'].mean().reset_index()
        ax.plot(season_avg['season'], season_avg['avg_ops'], marker='o', linewidth=2)
        ax.set_xlabel('Season')
        ax.set_ylabel('Average OPS')
        ax.set_title('League Average 9th Hitter OPS (2020-2026)')
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)
    with col2:
        if selected_team != "All":
            team_data = team_df[team_df['team_name'] == selected_team].sort_values('season')
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(team_data['season'], team_data['avg_ops'], marker='s', linewidth=2, color='green')
            league_avg = team_df[team_df['season'].isin(team_data['season'])].groupby('season')['avg_ops'].mean()
            ax.plot(league_avg.index, league_avg.values, linestyle='--', color='red', alpha=0.7, label='League Avg')
            ax.set_xlabel('Season')
            ax.set_ylabel('OPS')
            ax.set_title(f'{selected_team} 9th Hitter OPS Over Time')
            ax.legend()
            ax.grid(True, alpha=0.3)
            st.pyplot(fig)
        else:
            st.info("Select a team in the sidebar to see their trend")

# ----- Tab 3: Player Rankings -----
with tab3:
    st.header("Player Rankings (by Player ID)")
    st.caption("Note: Player names are not available due to ID mismatch. Shows player_id and their team.")
    col1, col2 = st.columns([3, 1])
    with col1:
        if selected_season != "All":
            display_players = player_df[player_df['season'] == int(selected_season)]
        else:
            display_players = player_df

        st.subheader("Most Frequent 9th Hitters")
        top_by_games = display_players.nlargest(15, 'games_batting_ninth')
        fig, ax = plt.subplots(figsize=(12, 8))
        bars = ax.barh(top_by_games['player_id'].astype(str) + ' (' + top_by_games['team_name'] + ')',
                       top_by_games['games_batting_ninth'], color='coral')
        ax.set_xlabel('Games Batting 9th')
        ax.set_title('Players with Most Games Batting 9th')
        plt.tight_layout()
        st.pyplot(fig)

        st.subheader("Top 9th Hitters by OPS (min 50 games)")
        top_by_ops = display_players[display_players['games_batting_ninth'] >= 50].nlargest(10, 'avg_ops')
        if not top_by_ops.empty:
            st.dataframe(top_by_ops[['player_id', 'team_name', 'season', 'games_batting_ninth',
                                     'avg_avg', 'avg_obp', 'avg_slg', 'avg_ops', 'total_rbi', 'total_runs']])
        else:
            st.info("No players with 50+ games batting 9th in the selected filter.")
    with col2:
        st.metric("Total Players (filtered)", len(display_players['player_id'].unique()))
        st.metric("Max Games by a Player", display_players['games_batting_ninth'].max() if not display_players.empty else 0)

# ----- Tab 4: 9th Hitter Impact -----
with tab4:
    st.header("How Often Do Teams Score When the 9th Hitter Reaches Base?")
    st.caption("Compares game outcomes based on whether the 9th hitter reached base (H, BB, HBP).")
    if not impact_df.empty:
        cols = st.columns(3)
        for i, status in enumerate(impact_df['ninth_hitter_status']):
            with cols[i % 3]:
                st.subheader(status)
                st.metric("Games", impact_df[impact_df['ninth_hitter_status'] == status]['games'].values[0])
                st.metric("Avg Total Runs", impact_df[impact_df['ninth_hitter_status'] == status]['avg_total_runs'].values[0])
                st.metric("High Scoring %", f"{impact_df[impact_df['ninth_hitter_status'] == status]['pct_high_scoring'].values[0]}%")
                st.metric("Home Win %", f"{impact_df[impact_df['ninth_hitter_status'] == status]['home_win_pct'].values[0]}%")
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(data=impact_df, x='ninth_hitter_status', y='avg_total_runs', palette='viridis', ax=ax)
        ax.set_ylabel('Average Total Runs per Game')
        ax.set_title('Average Runs Scored Based on 9th Hitter Performance')
        st.pyplot(fig)
        st.dataframe(impact_df)
    else:
        st.warning("No impact data available.")

# ----- Tab 5: Lineup Comparison -----
with tab5:
    st.header("Lineup Comparison: 9th Hitter vs. Other Positions")
    st.caption("Compare OPS across batting order positions for a selected season and team.")
    col1, col2 = st.columns(2)
    with col1:
        season_options = ["All"] + sorted(team_df['season'].unique(), reverse=True)
        selected_season_comp = st.selectbox("Select Season for Comparison", season_options, key="comp_season")
    with col2:
        team_options = ["All"] + sorted(team_df['team_name'].unique())
        selected_team_comp = st.selectbox("Select Team for Comparison", team_options, key="comp_team")

    season_filter = None if selected_season_comp == "All" else int(selected_season_comp)
    team_filter = None if selected_team_comp == "All" else selected_team_comp
    comp_df = load_lineup_comparison(season=season_filter, team=team_filter)

    if comp_df.empty:
        st.warning("No data found for the selected filters.")
    else:
        if selected_team_comp != "All":
            plot_df = comp_df[['batting_order', 'avg_ops']].drop_duplicates(subset=['batting_order'])
            plot_df = plot_df.sort_values('batting_order')
            label = f"{selected_team_comp} ({selected_season_comp})"
        else:
            plot_df = comp_df.groupby('batting_order').agg({
                'avg_ops': 'mean',
                'plate_appearances': 'sum'
            }).reset_index()
            label = f"League Average ({selected_season_comp})"

        colors = ['steelblue'] * 9
        colors[8] = 'crimson'  # position 9
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(plot_df['batting_order'], plot_df['avg_ops'], color=colors, edgecolor='black')
        ax.set_xlabel('Batting Order Position')
        ax.set_ylabel('OPS')
        ax.set_title(f'OPS by Batting Order Position - {label}')
        ax.set_xticks(range(1, 10))
        ax.set_ylim(0.5, 0.9)
        ax.axhline(y=plot_df['avg_ops'].mean(), color='gray', linestyle='--', alpha=0.5, label='Overall Avg')
        for bar, ops in zip(bars, plot_df['avg_ops']):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f'{ops:.3f}', ha='center', va='bottom', fontsize=9)
        ax.legend()
        plt.tight_layout()
        st.pyplot(fig)

        avg_1_8 = plot_df[plot_df['batting_order'] < 9]['avg_ops'].mean()
        ops_9 = plot_df[plot_df['batting_order'] == 9]['avg_ops'].values[0]
        gap = ops_9 - avg_1_8
        col1, col2, col3 = st.columns(3)
        col1.metric("9th Hitter OPS", f"{ops_9:.3f}")
        col2.metric("Avg OPS (1-8)", f"{avg_1_8:.3f}")
        col3.metric("Gap (9th - Avg 1-8)", f"{gap:+.3f}", delta_color="off")
        st.subheader("Data Table")
        st.dataframe(plot_df[['batting_order', 'avg_ops']])
        if selected_team_comp == "All":
            st.subheader("Team-Level Breakdown")
            team_summary = comp_df.groupby('team_name').apply(
                lambda x: pd.Series({
                    'ops_9': x[x['batting_order'] == 9]['avg_ops'].values[0] if not x[x['batting_order'] == 9].empty else None,
                    'avg_1_8': x[x['batting_order'] < 9]['avg_ops'].mean(),
                    'gap': (x[x['batting_order'] == 9]['avg_ops'].values[0] - x[x['batting_order'] < 9]['avg_ops'].mean()) if not x[x['batting_order'] == 9].empty else None
                })
            ).reset_index()
            st.dataframe(team_summary.sort_values('gap', ascending=False))

# ----- Tab 6: Impact Analysis (OPS + wOBA) -----
with tab6:
    st.header("Does a Better 9th Hitter Lead to More Runs?")
    st.caption("Team-season analysis using OPS and wOBA. Compare which metric better predicts run scoring.")
    if impact_analysis_df.empty:
        st.warning("No data available for impact analysis.")
    else:
        metric_choice = st.radio("Select metric to analyze", ["OPS", "wOBA"], horizontal=True)
        if metric_choice == "OPS":
            col_9 = 'ops_9'
            col_18 = 'ops_1_8'
            metric_name = "OPS"
        else:
            col_9 = 'wOBA_9'
            col_18 = 'wOBA_1_8'
            metric_name = "wOBA"

        fig, ax = plt.subplots(figsize=(12, 6))
        scatter = ax.scatter(impact_analysis_df[col_9], impact_analysis_df['runs_per_game'],
                             c=impact_analysis_df[col_18], cmap='viridis', alpha=0.7, edgecolors='black')
        ax.set_xlabel(f'{metric_name} (9th Hitter)')
        ax.set_ylabel('Runs per Game')
        ax.set_title(f'9th Hitter {metric_name} vs. Runs per Game (color = rest-of-lineup {metric_name})')
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label(f'{metric_name} (1-8)')
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)

        X = impact_analysis_df[[col_9, col_18]].values
        y = impact_analysis_df['runs_per_game'].values
        reg = LinearRegression().fit(X, y)
        coef_9, coef_18 = reg.coef_
        intercept = reg.intercept_
        r2 = reg.score(X, y)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric(f"Coefficient for 9th {metric_name}", f"{coef_9:.3f}",
                    help=f"Expected increase in runs per game for a 0.100 increase in 9th {metric_name}, holding other factors constant.")
        col2.metric(f"Coefficient for 1-8 {metric_name}", f"{coef_18:.3f}")
        col3.metric("R-squared", f"{r2:.3f}")
        col4.metric("Sample Size", len(impact_analysis_df))

        # Side-by-side coefficients
        st.subheader("Model Coefficients Comparison")
        X_ops = impact_analysis_df[['ops_9', 'ops_1_8']].values
        y_ops = impact_analysis_df['runs_per_game'].values
        reg_ops = LinearRegression().fit(X_ops, y_ops)
        X_woba = impact_analysis_df[['wOBA_9', 'wOBA_1_8']].values
        y_woba = impact_analysis_df['runs_per_game'].values
        reg_woba = LinearRegression().fit(X_woba, y_woba)
        coef_df = pd.DataFrame({
            'Metric': ['OPS', 'wOBA'],
            'Coefficient_9': [reg_ops.coef_[0], reg_woba.coef_[0]],
            'Coefficient_1_8': [reg_ops.coef_[1], reg_woba.coef_[1]],
            'R_squared': [reg_ops.score(X_ops, y_ops), reg_woba.score(X_woba, y_woba)]
        })
        st.dataframe(coef_df)

        # What-if
        st.subheader("What-If: Replace Your 9th Hitter")
        st.caption(f"Adjust the 9th hitter {metric_name} slider to see how many additional runs per game your team might score.")
        default_9 = impact_analysis_df[col_9].mean()
        default_18 = impact_analysis_df[col_18].mean()
        current_9 = st.slider(f"Current 9th hitter {metric_name}",
                              float(impact_analysis_df[col_9].min()), float(impact_analysis_df[col_9].max()),
                              float(default_9), 0.005)
        current_18 = st.slider(f"Current lineup (1-8) {metric_name}",
                               float(impact_analysis_df[col_18].min()), float(impact_analysis_df[col_18].max()),
                               float(default_18), 0.005)
        new_9 = st.slider(f"New 9th hitter {metric_name}",
                          float(impact_analysis_df[col_9].min()), float(impact_analysis_df[col_9].max()),
                          float(default_9 + 0.050), 0.005)
        current_runs = intercept + coef_9 * current_9 + coef_18 * current_18
        new_runs = intercept + coef_9 * new_9 + coef_18 * current_18
        diff = new_runs - current_runs
        st.metric("Estimated Runs per Game", f"{new_runs:.2f}", delta=f"{diff:+.2f}", delta_color="normal")
        st.caption(f"Current estimated runs per game: {current_runs:.2f}")
        st.subheader("Regression Equation")
        st.code(f"Runs per Game = {intercept:.3f} + ({coef_9:.3f} * 9th {metric_name}) + ({coef_18:.3f} * 1-8 {metric_name})")

        st.subheader("Team Data")
        st.dataframe(impact_analysis_df[['season', 'team_name', 'ops_9', 'ops_1_8', 'wOBA_9', 'wOBA_1_8', 'runs_per_game']])

# ----- Tab 7: Data Table -----
with tab7:
    st.header("Data Table")
    search = st.text_input("Search for team...")
    if search:
        display_df = filtered_team_df[filtered_team_df['team_name'].str.contains(search, case=False)]
    else:
        display_df = filtered_team_df
    st.dataframe(display_df.sort_values('avg_ops', ascending=False))
    csv = display_df.to_csv(index=False).encode('utf-8')
    st.download_button(label="📥 Download CSV", data=csv, file_name='9th_hitter_data.csv', mime='text/csv')

# Sidebar footer
st.sidebar.markdown("---")
st.sidebar.caption("Data source: MLB Stats API")
st.sidebar.caption("Seasons: 2020-2026")