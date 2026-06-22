import sqlite3
import csv

DB_PATH = 'data/mlb_data.db'
CSV_PATH = 'data/mlb_games_full.csv'

# Connect to database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Get all games
cursor.execute('''
SELECT 
    g.game_id, g.game_pk, g.game_date, g.season, g.game_type, g.status,
    t1.team_name as home_team, t2.team_name as away_team,
    g.home_score, g.away_score, g.venue_name, g.weather_condition, g.weather_temp, g.wind, g.attendance, g.game_duration_minutes
FROM games g
JOIN teams t1 ON g.home_team_id = t1.team_id
JOIN teams t2 ON g.away_team_id = t2.team_id
WHERE g.game_type != 'S'
ORDER BY g.season, g.game_date, g.game_pk
''')
games = cursor.fetchall()

# Prepare CSV header
header = [
    'game_id', 'game_pk', 'game_date', 'season', 'game_type', 'status',
    'home_team', 'away_team', 'home_score', 'away_score', 'venue_name',
    'weather_condition', 'weather_temp', 'wind', 'attendance', 'game_duration_minutes',
    'home_at_bats', 'home_runs', 'home_hits', 'home_doubles', 'home_triples', 'home_home_runs', 'home_rbi', 'home_walks', 'home_strikeouts', 'home_stolen_bases',
    'away_at_bats', 'away_runs', 'away_hits', 'away_doubles', 'away_triples', 'away_home_runs', 'away_rbi', 'away_walks', 'away_strikeouts', 'away_stolen_bases',
    'home_innings_pitched', 'home_hits_allowed', 'home_runs_allowed', 'home_earned_runs', 'home_pitching_walks', 'home_pitching_strikeouts', 'home_home_runs_allowed',
    'away_innings_pitched', 'away_hits_allowed', 'away_runs_allowed', 'away_earned_runs', 'away_pitching_walks', 'away_pitching_strikeouts', 'away_home_runs_allowed'
]

# Helper to aggregate stats for a team in a game
def aggregate_stats(table, game_id, team_id):
    if table == 'box_scores_batting':
        cursor.execute(f'''
            SELECT 
                SUM(at_bats), SUM(runs), SUM(hits), SUM(doubles), SUM(triples), SUM(home_runs),
                SUM(rbi), SUM(walks), SUM(strikeouts), SUM(stolen_bases)
            FROM {table}
            WHERE game_id=? AND team_id=?
        ''', (game_id, team_id))
        row = cursor.fetchone()
        return {
            'at_bats': row[0] or 0,
            'runs': row[1] or 0,
            'hits': row[2] or 0,
            'doubles': row[3] or 0,
            'triples': row[4] or 0,
            'home_runs': row[5] or 0,
            'rbi': row[6] or 0,
            'walks': row[7] or 0,
            'strikeouts': row[8] or 0,
            'stolen_bases': row[9] or 0
        }
    elif table == 'box_scores_pitching':
        cursor.execute(f'''
            SELECT 
                SUM(innings_pitched), SUM(hits_allowed), SUM(runs_allowed), SUM(earned_runs),
                SUM(walks), SUM(strikeouts), SUM(home_runs_allowed)
            FROM {table}
            WHERE game_id=? AND team_id=?
        ''', (game_id, team_id))
        row = cursor.fetchone()
        return {
            'innings_pitched': row[0] or 0,
            'hits_allowed': row[1] or 0,
            'runs_allowed': row[2] or 0,
            'earned_runs': row[3] or 0,
            'walks': row[4] or 0,
            'strikeouts': row[5] or 0,
            'home_runs_allowed': row[6] or 0
        }
    return {}

# Write to CSV
with open(CSV_PATH, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=header)
    writer.writeheader()
    for g in games:
        game_id = g[0]
        home_team_id = None
        away_team_id = None
        # Get team IDs
        cursor.execute('SELECT home_team_id, away_team_id FROM games WHERE game_id=?', (game_id,))
        ids = cursor.fetchone()
        if ids:
            home_team_id, away_team_id = ids
        home_batting = aggregate_stats('box_scores_batting', game_id, home_team_id)
        away_batting = aggregate_stats('box_scores_batting', game_id, away_team_id)
        home_pitching = aggregate_stats('box_scores_pitching', game_id, home_team_id)
        away_pitching = aggregate_stats('box_scores_pitching', game_id, away_team_id)
        row = dict(zip(header[:16], g))
        # Home batting
        row['home_at_bats'] = home_batting['at_bats']
        row['home_runs'] = home_batting['runs']
        row['home_hits'] = home_batting['hits']
        row['home_doubles'] = home_batting['doubles']
        row['home_triples'] = home_batting['triples']
        row['home_home_runs'] = home_batting['home_runs']
        row['home_rbi'] = home_batting['rbi']
        row['home_walks'] = home_batting['walks']
        row['home_strikeouts'] = home_batting['strikeouts']
        row['home_stolen_bases'] = home_batting['stolen_bases']
        # Away batting
        row['away_at_bats'] = away_batting['at_bats']
        row['away_runs'] = away_batting['runs']
        row['away_hits'] = away_batting['hits']
        row['away_doubles'] = away_batting['doubles']
        row['away_triples'] = away_batting['triples']
        row['away_home_runs'] = away_batting['home_runs']
        row['away_rbi'] = away_batting['rbi']
        row['away_walks'] = away_batting['walks']
        row['away_strikeouts'] = away_batting['strikeouts']
        row['away_stolen_bases'] = away_batting['stolen_bases']
        # Home pitching
        row['home_innings_pitched'] = home_pitching['innings_pitched']
        row['home_hits_allowed'] = home_pitching['hits_allowed']
        row['home_runs_allowed'] = home_pitching['runs_allowed']
        row['home_earned_runs'] = home_pitching['earned_runs']
        row['home_pitching_walks'] = home_pitching['walks']
        row['home_pitching_strikeouts'] = home_pitching['strikeouts']
        row['home_home_runs_allowed'] = home_pitching['home_runs_allowed']
        # Away pitching
        row['away_innings_pitched'] = away_pitching['innings_pitched']
        row['away_hits_allowed'] = away_pitching['hits_allowed']
        row['away_runs_allowed'] = away_pitching['runs_allowed']
        row['away_earned_runs'] = away_pitching['earned_runs']
        row['away_pitching_walks'] = away_pitching['walks']
        row['away_pitching_strikeouts'] = away_pitching['strikeouts']
        row['away_home_runs_allowed'] = away_pitching['home_runs_allowed']
        writer.writerow(row)

conn.close()
print(f"Exported {len(games)} games to {CSV_PATH}")
