import sqlite3
import statsapi
import time

DB_PATH = '../data/mlb_data.db'

def check_game_has_data(game_id):
    """Check if a game has batting order data in the API"""
    try:
        boxscore = statsapi.boxscore_data(str(game_id))
        if not boxscore or 'gameId' not in boxscore:
            return False
        
        # Check if there are any battingOrder values
        for team_type in ['away', 'home']:
            if team_type not in boxscore:
                continue
            
            players = boxscore.get(team_type, {}).get('players', {})
            for player_key, player_data in players.items():
                batting_spot = player_data.get('battingOrder')
                if batting_spot is not None:
                    try:
                        batting_spot = int(batting_spot)
                        if batting_spot in [100, 200, 300, 400, 500, 600, 700, 800, 900]:
                            return True
                    except (ValueError, TypeError):
                        continue
        return False
    except:
        return False

def mark_missing_games(limit=None):
    """Mark games without batting order data as skipped (batting_order = 0)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get games that need batting order
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
    print(f"Checking {total} games...")
    print("-" * 50)
    
    marked = 0
    failed = 0
    
    for idx, (game_id,) in enumerate(games, 1):
        print(f"\n[{idx}/{total}] Checking game {game_id}...")
        
        if check_game_has_data(game_id):
            print(f"  ✅ Game has data - leaving as NULL (will be processed later)")
        else:
            # Mark as skipped (batting_order = 0)
            cursor.execute("""
                UPDATE box_scores_batting 
                SET batting_order = 0 
                WHERE game_id = ? AND batting_order IS NULL
            """, (game_id,))
            marked += 1
            print(f"  ⚠️ No data - marked as skipped")
        
        if idx % 50 == 0:
            conn.commit()
            print(f"\nProgress: {idx}/{total} games checked, {marked} marked as skipped")
        
        time.sleep(0.1)
    
    conn.commit()
    print("\n" + "=" * 50)
    print(f"Complete!")
    print(f"  Games checked: {total}")
    print(f"  Marked as skipped: {marked}")
    print(f"  Failed: {failed}")
    print("=" * 50)
    
    conn.close()

def show_progress():
    """Show current progress"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            COUNT(DISTINCT CASE WHEN batting_order > 0 THEN game_id END) as with_data,
            COUNT(DISTINCT CASE WHEN batting_order = 0 THEN game_id END) as skipped,
            COUNT(DISTINCT CASE WHEN batting_order IS NULL THEN game_id END) as no_data
        FROM box_scores_batting 
    """)
    stats = cursor.fetchone()
    
    total = stats[0] + stats[1] + stats[2]
    pct = (stats[0] / total * 100) if total > 0 else 0
    
    print(f"\nCurrent Progress:")
    print(f"  Games with batting order: {stats[0]}")
    print(f"  Games skipped (no data): {stats[1]}")
    print(f"  Games without data: {stats[2]}")
    print(f"  Total games: {total}")
    print(f"  Progress: {pct:.1f}%")
    
    conn.close()

if __name__ == "__main__":
    print("=" * 50)
    print("Mark Missing Games as Skipped")
    print("=" * 50)
    print(f"Database path: {DB_PATH}")
    print()
    
    show_progress()
    print()
    
    response = input("How many games to check? (enter 'all' or a number): ")
    
    if response.strip().lower() == 'all':
        limit = None
    else:
        try:
            limit = int(response) if response.strip() else 50
        except ValueError:
            print("Invalid input. Using default of 50.")
            limit = 50
    
    mark_missing_games(limit=limit)
    
    print("\n" + "=" * 50)
    show_progress()