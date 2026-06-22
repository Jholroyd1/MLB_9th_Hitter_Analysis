#!/usr/bin/env python3
"""
Backfill script for games missing both box score batting and pitching data.
Reads game_ids from missing_boxscore_game_ids.txt and runs get_all_games_stats.py for each.
"""
game_ids = []
import subprocess
import time
import sqlite3

# Path to the MLB database
DB_PATH = '../data/mlb_data.db'

game_ids = []
with open('../data/missing_boxscore_game_ids.txt') as f:
    for line in f:
        line = line.strip()
        if line.isdigit():
            game_ids.append(line)

# Connect to the database to look up seasons
def get_season(game_id):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute('SELECT season FROM games WHERE game_id = ?', (game_id,))
        row = cur.fetchone()
        return str(row[0]) if row else None

for gid in game_ids:
    season = get_season(gid)
    if not season:
        print(f"Could not find season for game_id {gid}, skipping.")
        continue
    print(f"Backfilling game_id: {gid} (season {season})")
    subprocess.run([
        '../.venv/bin/python',
        'get_all_games_stats.py',
        '--game_id',
        gid,
        '--season',
        season
    ])
    time.sleep(1)  # avoid hammering the API
print("Backfill complete.")
