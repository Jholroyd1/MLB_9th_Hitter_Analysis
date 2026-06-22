import sqlite3
import pandas as pd

DB_PATH = 'data/mlb_data.db'

def export_csv(query, filename):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(query, conn)
    df.to_csv(f'data/{filename}.csv', index=False)
    conn.close()
    print(f"✅ Exported {filename}.csv ({len(df)} rows)")

# 1. Team-level 9th hitter stats
export_csv("""
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
""", "team_9th_hitter_data")

# 2. Player-level 9th hitter data
export_csv("""
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
""", "player_9th_hitter_data")

# 3. Impact data (9th hitter reaching base)
export_csv("""
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
    ROUND(100.0 * SUM(CASE WHEN g.away_score > g.home_score THEN 1 ELSE 0 END) / COUNT(*), 1) as away_win_pct
FROM ninth_hitter_games nhg
JOIN games g ON nhg.game_id = g.game_id
GROUP BY nhg.ninth_hitter_status
ORDER BY avg_total_runs DESC;
""", "impact_data")

# 4. Lineup comparison data (OPS by batting order)
export_csv("""
SELECT 
    t.team_name,
    g.season,
    bb.batting_order,
    COUNT(*) as plate_appearances,
    ROUND((SUM(bb.hits) + SUM(bb.walks) + SUM(bb.hit_by_pitch)) * 1.0 / 
          NULLIF(SUM(bb.at_bats) + SUM(bb.walks) + SUM(bb.hit_by_pitch) + SUM(bb.sacrifice_flies), 0), 3) as obp,
    ROUND((SUM(bb.hits) + SUM(bb.doubles) + 2*SUM(bb.triples) + 3*SUM(bb.home_runs)) * 1.0 / 
          NULLIF(SUM(bb.at_bats), 0), 3) as slg,
    ROUND(
        ((SUM(bb.hits) + SUM(bb.walks) + SUM(bb.hit_by_pitch)) * 1.0 / 
         NULLIF(SUM(bb.at_bats) + SUM(bb.walks) + SUM(bb.hit_by_pitch) + SUM(bb.sacrifice_flies), 0)) +
        ((SUM(bb.hits) + SUM(bb.doubles) + 2*SUM(bb.triples) + 3*SUM(bb.home_runs)) * 1.0 / 
         NULLIF(SUM(bb.at_bats), 0)), 
    3) as ops
FROM box_scores_batting bb
JOIN games g ON bb.game_id = g.game_id
LEFT JOIN teams t ON bb.team_id = t.team_id
WHERE bb.batting_order BETWEEN 1 AND 9
  AND bb.at_bats > 0
GROUP BY t.team_name, g.season, bb.batting_order
ORDER BY g.season, t.team_name, bb.batting_order;
""", "lineup_comparison")

print("\n✅ All CSV files exported to data/ folder")