import sqlite3
import statsapi
import time

DB_PATH = '../data/mlb_data.db'

def backfill_game(game_id):
    """Update batting order for a game"""
    try:
        # Get the boxscore data
        boxscore = statsapi.boxscore_data(str(game_id))
        if not boxscore or 'gameId' not in boxscore:
            return False
        
        # Get batting order from API
        api_order = []
        for team_type in ['away', 'home']:
            if team_type not in boxscore:
                continue
            
            players = boxscore.get(team_type, {}).get('players', {})
            
            # Collect all players with battingOrder
            team_order = []
            for player_key, player_data in players.items():
                batting_spot = player_data.get('battingOrder')
                if batting_spot is not None:
                    try:
                        batting_spot = int(batting_spot)
                        if batting_spot in [100, 200, 300, 400, 500, 600, 700, 800, 900]:
                            order = int(batting_spot / 100)
                            team_order.append((order, player_key))
                    except (ValueError, TypeError):
                        continue
            
            # Sort by batting order
            team_order.sort(key=lambda x: x[0])
            api_order.extend(team_order)
        
        if not api_order:
            return False
        
        # Now update the database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get all players for this game from database
        cursor.execute("""
            SELECT player_id 
            FROM box_scores_batting 
            WHERE game_id = ?
        """, (game_id,))
        db_players = [row[0] for row in cursor.fetchall()]
        
        if not db_players:
            conn.close()
            return False
        
        # Update based on position in the data
        for i, (order, player_key) in enumerate(api_order):
            if i >= len(db_players):
                break
            
            # Use the database player ID at position i
            db_player_id = db_players[i]
            
            # Update the batting order
            cursor.execute("""
                UPDATE box_scores_batting 
                SET batting_order = ? 
                WHERE game_id = ? AND player_id = ?
            """, (order, game_id, db_player_id))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        return False

def backfill_games(limit=None):
    """Backfill batting order for games"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get games that need batting order
    if limit is None:
        # Process all games
        cursor.execute("""
            SELECT DISTINCT bb.game_id 
            FROM box_scores_batting bb
            INNER JOIN games g ON bb.game_id = g.game_id
            WHERE bb.batting_order IS NULL
            ORDER BY bb.game_id
        """)
    else:
        cursor.execute("""
            SELECT DISTINCT bb.game_id 
            FROM box_scores_batting bb
            INNER JOIN games g ON bb.game_id = g.game_id
            WHERE bb.batting_order IS NULL
            ORDER BY bb.game_id
            LIMIT ?
        """, (limit,))
    
    games = cursor.fetchall()
    total = len(games)
    
    if total == 0:
        print("All games already have batting order data!")
        conn.close()
        return
    
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
        
        # Show progress every 10 games
        if idx % 10 == 0:
            print(f"\nProgress: {idx}/{total} games processed")
            # Check how many games now have batting order
            cursor.execute("""
                SELECT COUNT(DISTINCT game_id) 
                FROM box_scores_batting 
                WHERE batting_order IS NOT NULL
            """)
            current = cursor.fetchone()[0]
            print(f"Games with batting order: {current}")
        
        time.sleep(0.1)  # Small delay to avoid rate limiting
    
    print("\n" + "=" * 50)
    print(f"Complete!")
    print(f"  Updated: {updated} games")
    print(f"  Skipped: {skipped} games")
    print("=" * 50)
    
    conn.close()

def verify_game(game_id):
    """Verify a specific game"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT player_id, batting_order 
        FROM box_scores_batting 
        WHERE game_id = ?
        AND batting_order IS NOT NULL
        ORDER BY batting_order
    """, (game_id,))
    
    results = cursor.fetchall()
    print(f"\nVerification for game {game_id}:")
    if results:
        for player_id, order in results:
            print(f"  Position {order}: Player {player_id}")
    else:
        print("  No batting order data found")
    
    conn.close()

def show_progress():
    """Show current progress"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT COUNT(DISTINCT game_id) 
        FROM box_scores_batting 
        WHERE batting_order IS NOT NULL
    """)
    games_with_order = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(DISTINCT bb.game_id) 
        FROM box_scores_batting bb
        INNER JOIN games g ON bb.game_id = g.game_id
        WHERE bb.batting_order IS NULL
    """)
    games_without_order = cursor.fetchone()[0]
    
    total = games_with_order + games_without_order
    pct = (games_with_order / total * 100) if total > 0 else 0
    
    print(f"\nCurrent Progress:")
    print(f"  Games with batting order: {games_with_order}")
    print(f"  Games without: {games_without_order}")
    print(f"  Total games: {total}")
    print(f"  Progress: {pct:.1f}%")
    
    conn.close()

if __name__ == "__main__":
    print("=" * 50)
    print("Batting Order Backfill (All Games)")
    print("=" * 50)
    print(f"Database path: {DB_PATH}")
    print()
    
    # Show current progress
    show_progress()
    print()
    
    response = input("How many games to process? (enter 'all' for all, or a number): ")
    
    if response.strip().lower() == 'all':
        limit = None
    else:
        try:
            limit = int(response) if response.strip() else 50
        except ValueError:
            print("Invalid input. Using default of 50.")
            limit = 50
    
    backfill_games(limit=limit)
    
    # Show final progress
    print("\n" + "=" * 50)
    show_progress()
    
    # Verify the first game
    verify_game(2457)