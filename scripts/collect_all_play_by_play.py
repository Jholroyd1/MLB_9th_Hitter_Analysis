"""
Collect play-by-play data for all games in the database
"""
import sqlite3
import statsapi
import time

DB_PATH = 'data/mlb_data.db'
LOG_PATH = 'logs/collect_pbp.log'

def collect_pbp_for_all_games():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT game_pk, game_id FROM games')
    games = cursor.fetchall()
    conn.close()
    print(f"Found {len(games)} games.")
    inserted_total = 0
    # Dynamically get play_by_play columns, excluding id
    conn_schema = sqlite3.connect(DB_PATH)
    cursor_schema = conn_schema.cursor()
    cursor_schema.execute('PRAGMA table_info(play_by_play)')
    all_columns = [col[1] for col in cursor_schema.fetchall()]
    insert_columns = [col for col in all_columns if col != 'id']
    insert_sql = f"INSERT INTO play_by_play ({', '.join(insert_columns)}) VALUES ({', '.join(['?']*len(insert_columns))})"
    conn_schema.close()

    for idx, (game_pk, game_id) in enumerate(games, 1):
        try:
            pbp = statsapi.get('game_playByPlay', {'gamePk': game_pk})
            all_plays = pbp.get('allPlays', [])
            if not all_plays:
                print(f"[{idx}/{len(games)}] No play-by-play for game {game_pk}")
                continue
            conn2 = sqlite3.connect(DB_PATH)
            cursor2 = conn2.cursor()
            for play in all_plays:
                event = play.get('result', {})
                matchup = play.get('matchup', {})
                pitch = play.get('pitchData', {})
                runners = play.get('runners', [])
                inning = play.get('about', {}).get('inning')
                half_inning = play.get('about', {}).get('halfInning')
                at_bat_index = play.get('atBatIndex')
                pitch_number = play.get('playEndTime', None)
                event_type = event.get('eventType')
                event_description = event.get('description')
                result_type = event.get('type')
                batter_id = matchup.get('batter', {}).get('id')
                pitcher_id = matchup.get('pitcher', {}).get('id')
                runner_on_first_id = None
                runner_on_second_id = None
                runner_on_third_id = None
                if runners:
                    for r in runners:
                        base = r.get('movement', {}).get('end')
                        if base == '1B':
                            runner_on_first_id = r.get('details', {}).get('runner', {}).get('id')
                        elif base == '2B':
                            runner_on_second_id = r.get('details', {}).get('runner', {}).get('id')
                        elif base == '3B':
                            runner_on_third_id = r.get('details', {}).get('runner', {}).get('id')
                outs = play.get('count', {}).get('outs')
                balls = play.get('count', {}).get('balls')
                strikes = play.get('count', {}).get('strikes')
                count_str = f"{balls}-{strikes}" if balls is not None and strikes is not None else None
                pitch_type = pitch.get('pitchType') if pitch else None
                pitch_speed = pitch.get('startSpeed') if pitch else None
                runs_scored = event.get('runners', [{}])[0].get('runs', 0) if event.get('runners') else 0
                rbi = event.get('rbi', 0)

                # Extract batted ball (hitData) from playEvents
                hitData = None
                if 'playEvents' in play:
                    for ev in play['playEvents']:
                        if 'hitData' in ev and ev['hitData']:
                            hitData = ev['hitData']
                            break
                launch_speed = hitData.get('launchSpeed') if hitData else None
                launch_angle = hitData.get('launchAngle') if hitData else None
                total_distance = hitData.get('totalDistance') if hitData else None
                trajectory = hitData.get('trajectory') if hitData else None
                hardness = hitData.get('hardness') if hitData else None
                location = hitData.get('location') if hitData else None
                coord_x = hitData.get('coordinates', {}).get('coordX') if hitData and 'coordinates' in hitData else None
                coord_y = hitData.get('coordinates', {}).get('coordY') if hitData and 'coordinates' in hitData else None

                # Build values list in the same order as insert_columns
                values = [
                    game_id,
                    play.get('playId'),
                    inning,
                    half_inning,
                    at_bat_index,
                    pitch_number,
                    event_type,
                    event_description,
                    result_type,
                    batter_id,
                    pitcher_id,
                    runner_on_first_id,
                    runner_on_second_id,
                    runner_on_third_id,
                    outs,
                    balls,
                    strikes,
                    count_str,
                    pitch_type,
                    pitch_speed,
                    runs_scored,
                    rbi,
                    launch_speed,
                    launch_angle,
                    total_distance,
                    trajectory,
                    hardness,
                    location,
                    coord_x,
                    coord_y,
                    None  # created_at
                ]
                # Truncate or pad values to match insert_columns length
                values = values[:len(insert_columns)]
                while len(values) < len(insert_columns):
                    values.append(None)
                cursor2.execute(insert_sql, values)
            conn2.commit()
            conn2.close()
            inserted_total += len(all_plays)
            print(f"[{idx}/{len(games)}] Inserted {len(all_plays)} plays for game {game_pk}")
            time.sleep(0.5)
        except Exception as e:
            print(f"[{idx}/{len(games)}] Error for game {game_pk}: {e}")
            continue
    print(f"Inserted total {inserted_total} play-by-play events.")

if __name__ == '__main__':
    collect_pbp_for_all_games()
