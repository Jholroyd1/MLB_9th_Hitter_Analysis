"""
Check MLB Data Collection Status
"""

import sqlite3

DB_PATH = "../data/mlb_data.db"

conn = sqlite3.connect(DB_PATH)

print("\n" + "="*70)
print(" MLB DATABASE STATUS")
print("="*70)

# Teams
team_count = conn.execute("SELECT COUNT(*) FROM teams").fetchone()[0]
print(f"\nTeams: {team_count}")

# Games by season
print("\nGames by Season:")
seasons = conn.execute("""
    SELECT season, COUNT(*) as games, 
           SUM(CASE WHEN status IN ('Final', 'Completed', 'Game Over') THEN 1 ELSE 0 END) as completed
    FROM games
    GROUP BY season
    ORDER BY season DESC
""").fetchall()

for season, games, completed in seasons:
    print(f"  {season}: {games} games ({completed} completed)")

# Total stats
batting_stats = conn.execute("SELECT COUNT(*) FROM box_scores_batting").fetchone()[0]
pitching_stats = conn.execute("SELECT COUNT(*) FROM box_scores_pitching").fetchone()[0]

print(f"\nPlayer Stats:")
print(f"  Batting records: {batting_stats:,}")
print(f"  Pitching records: {pitching_stats:,}")

# Games with stats
games_with_stats = conn.execute("""
    SELECT COUNT(DISTINCT game_id) 
    FROM box_scores_batting
""").fetchone()[0]

total_completed = conn.execute("""
    SELECT COUNT(*) FROM games 
    WHERE status IN ('Final', 'Completed', 'Game Over')
""").fetchone()[0]

print(f"\nCoverage:")
print(f"  Games with box scores: {games_with_stats}")
print(f"  Total completed games: {total_completed}")
if total_completed > 0:
    print(f"  Coverage: {games_with_stats/total_completed*100:.1f}%")

# Recent games
print("\nMost Recent Games:")
recent = conn.execute("""
    SELECT game_pk, game_date, status
    FROM games
    ORDER BY game_date DESC, game_pk DESC
    LIMIT 5
""").fetchall()

for game_pk, game_date, status in recent:
    print(f"  {game_date} - Game {game_pk} ({status})")

print("="*70 + "\n")

conn.close()
