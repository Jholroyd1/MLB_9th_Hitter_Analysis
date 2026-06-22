#!/usr/bin/env python3
"""
Backfill script for games missing play-by-play data.
Reads game_ids from missing_playbyplay_game_ids.txt, looks up the season for each,
and runs get_all_games_stats.py for each game_id/season pair.
"""
import subprocess
import time
import sqlite3

DB_PATH = '../data/mlb_data.db'

game_ids = []
with open('../data/missing_playbyplay_game_ids.txt') as f:
    for line in f:
        line = line.strip()
        if line.isdigit():
            game_ids.append(line)

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
    print(f"Backfilling play-by-play for game_id: {gid} (season {season})")
    subprocess.run([
        '../.venv/bin/python',
        'get_all_games_stats.py',
        '--game_id',
        gid,
        '--season',
        season
    ])
    time.sleep(1)
print("Play-by-play backfill complete.")
