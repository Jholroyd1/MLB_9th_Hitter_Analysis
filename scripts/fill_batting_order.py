import sqlite3
import statsapi
import time

DB_PATH = '../data/mlb_data.db'

def backfill_game(game_id):
    """Update batting order for a game by position"""
    try:
        boxscore = statsapi.boxscore_data(str(game_id))
        if not boxscore or 'gameId' not in boxscore:
            return False
        
        # Get batting order from API (list of player IDs)
        api_order = []
        for team_type in ['away', 'home']:
            if team_type not in boxscore:
                continue
            players = boxscore.get(team_type, {}).get('players', {})
            team_order = []
            for player_key, player_data in players.items():
                batting_spot = player_data.get('battingOrder')
                if batting_spot is not None:
                    try:
                        batting_spot = int(batting_spot)
                        if batting_spot in [100, 200, 300, 400, 500, 600, 700, 800, 900]:
                            order = int(batting_spot / 100)
                            # Use the player_key (e.g., 'ID116706')
                            team_order.append((order, player_key))
                    except (ValueError, TypeError):
                        continue
            team_order.sort(key=lambda x: x[0])
            api_order.extend(team_order)
        
        if not api_order:
            return False
        
        # Get all rows for this game
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT rowid, player_id
            FROM box_scores_batting
            WHERE game_id = ?
            ORDER BY rowid
        """, (game_id,))
        db_players = cursor.fetchall()
        
        if len(db_players) < 18:
            conn.close()
            return False
        
        # Update first 18 rows with batting order positions
        for i in range(min(18, len(api_order))):
            order, api_id = api_order[i]
            rowid = db_players[i][0]
            cursor.execute("""
                UPDATE box_scores_batting
                SET batting_order = ?
                WHERE rowid = ?
            """, (order, rowid))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        return False

def backfill_games(limit=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if limit is None:
        cursor.execute("""
            SELECT DISTINCT game_id
            FROM box_scores_batting
            WHERE batting_order IS NULL
            ORDER BY game_id
        """)
    else:
        cursor.execute("""
            SELECT DISTINCT game_id
            FROM box_scores_batting
            WHERE batting_order IS NULL
            ORDER BY game_id
            LIMIT ?
        """, (limit,))
    
    games = cursor.fetchall()
    total = len(games)
    print(f"Processing {total} games...")
    print("-" * 50)
    
    updated = 0
    skipped = 0
    
    for idx, (game_id,) in enumerate(games, 1):
        print(f"\n[{idx}/{total}] Game {game_id}...")
        if backfill_game(game_id):
            updated += 1
            print(f"  ✅ Updated game {game_id}")
        else:
            skipped += 1
            print(f"  ⚠️ No data for game {game_id}")
        time.sleep(0.1)
    
    print("\n" + "=" * 50)
    print(f"Complete!")
    print(f"  Updated: {updated}")
    print(f"  Skipped: {skipped}")
    print("=" * 50)
    conn.close()

if __name__ == "__main__":
    print("=" * 50)
    print("Backfill by Position (First 18 rows)")
    print("=" * 50)
    response = input("How many games to process? (enter 'all' or a number): ")
    if response.strip().lower() == 'all':
        backfill_games(limit=None)
    else:
        try:
            limit = int(response)
            backfill_games(limit=limit)
        except ValueError:
            print("Invalid input. Using default of 50.")
            backfill_games(limit=50)