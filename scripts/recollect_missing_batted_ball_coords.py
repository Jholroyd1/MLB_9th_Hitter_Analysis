#!/usr/bin/env python3
"""
Recollect missing batted ball coordinate data for specific play_by_play events.
Reads missing_batted_ball_coords.csv, fetches play-by-play for each game, and attempts to update coord_x/coord_y for the specified at_bat_index.
"""
import csv
import sqlite3
import statsapi
import time

DB_PATH = '../data/mlb_data.db'
CSV_PATH = '../data/missing_batted_ball_coords.csv'

def get_game_play_by_play(game_id):
    try:
        pbp = statsapi.get('game_playByPlay', {'gamePk': int(game_id)})
        return pbp.get('allPlays', [])
    except Exception as e:
        print(f"Error fetching play-by-play for game {game_id}: {e}")
        return []

def update_coords(game_id, at_bat_index, coord_x, coord_y):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE play_by_play
            SET coord_x = ?, coord_y = ?
            WHERE game_id = ? AND at_bat_index = ?
            """,
            (coord_x, coord_y, game_id, at_bat_index)
        )
        conn.commit()

def main():
    with open(CSV_PATH) as f:
        reader = csv.reader(f, delimiter='|')
        for row in reader:
            game_id, at_bat_index = row[0], row[1]
            all_plays = get_game_play_by_play(game_id)
            play = next((p for p in all_plays if str(p.get('atBatIndex')) == at_bat_index), None)
            if not play:
                print(f"No play found for game {game_id} at_bat_index {at_bat_index}")
                continue
            hit_data = play.get('hitData') or play.get('hitData', {})
            coord_x = hit_data.get('coordinates', {}).get('coordX')
            coord_y = hit_data.get('coordinates', {}).get('coordY')
            if coord_x is not None and coord_y is not None:
                update_coords(game_id, at_bat_index, coord_x, coord_y)
                print(f"Updated coords for game {game_id} at_bat_index {at_bat_index}: x={coord_x}, y={coord_y}")
            else:
                print(f"No coordinates found for game {game_id} at_bat_index {at_bat_index}")
            time.sleep(0.5)

if __name__ == "__main__":
    main()
