"""
Backfill players table from box_scores_batting and box_scores_pitching
"""
import sqlite3
import statsapi

DB_PATH = 'data/mlb_data.db'

def get_player_info(player_id):
    try:
        data = statsapi.get('person', {'personId': player_id})
        person = data.get('people', [{}])[0]
        return {
            'player_id': player_id,
            'full_name': person.get('fullName', ''),
            'first_name': person.get('firstName', ''),
            'last_name': person.get('lastName', ''),
            'position': person.get('primaryPosition', {}).get('abbreviation', ''),
            'bat_side': person.get('batSide', {}).get('code', ''),
            'pitch_hand': person.get('pitchHand', {}).get('code', '')
        }
    except Exception:
        return None

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Get all unique player_ids from box_scores_batting and box_scores_pitching
    cursor.execute('SELECT DISTINCT player_id FROM box_scores_batting')
    batting_ids = set(row[0] for row in cursor.fetchall())
    cursor.execute('SELECT DISTINCT player_id FROM box_scores_pitching')
    pitching_ids = set(row[0] for row in cursor.fetchall())
    all_ids = batting_ids | pitching_ids
    print(f"Found {len(all_ids)} unique player IDs to backfill.")
    inserted = 0
    for player_id in all_ids:
        info = get_player_info(player_id)
        if info and info['full_name']:
            cursor.execute('''
                INSERT OR IGNORE INTO players (
                    player_id, full_name, first_name, last_name, position, bat_side, pitch_hand
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                info['player_id'],
                info['full_name'],
                info['first_name'],
                info['last_name'],
                info['position'],
                info['bat_side'],
                info['pitch_hand']
            ))
            inserted += 1
    conn.commit()
    conn.close()
    print(f"Inserted {inserted} player records into players table.")

if __name__ == '__main__':
    main()
