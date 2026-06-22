"""
MLB Data Collector
Collects game schedules, box scores, and player stats from MLB Stats API
"""

import sqlite3
import statsapi
from datetime import datetime, timedelta
import time
import argparse


DB_PATH = "/Users/jackholroyd/Desktop/MLB-Stats-Collection-and-Spray-Charts-main/data/mlb_data.db"


class MLBDataCollector:
    """Collect MLB data using statsapi library"""
    
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        
    def collect_teams(self):
        """Collect all MLB teams"""
        print("\n" + "="*70)
        print(" COLLECTING TEAMS")
        print("="*70)
        
        # Get all teams
        teams_data = statsapi.get('teams', {'sportId': 1})  # 1 = MLB
        teams = teams_data.get('teams', [])
        
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        cursor = conn.cursor()
        
        inserted = 0
        for team in teams:
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO teams (
                        team_id, team_name, team_abbr, division, league
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    team['id'],
                    team['name'],
                    team.get('abbreviation', team.get('fileCode', '')),
                    team.get('division', {}).get('name', ''),
                    team.get('league', {}).get('name', '')
                ))
                inserted += 1
            except Exception as e:
                print(f"Error inserting team {team.get('name')}: {e}")
        
        conn.commit()
        conn.close()
        
        print(f"✅ Inserted {inserted} teams")
        return inserted
    
    def collect_schedule(self, start_date, end_date):
        """Collect games schedule for date range"""
        print(f"\n{'='*70}")
        print(f" COLLECTING SCHEDULE: {start_date} to {end_date}")
        print(f"{'='*70}")
        
        # Get schedule
        schedule = statsapi.schedule(start_date=start_date, end_date=end_date)
        
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        cursor = conn.cursor()
        
        inserted = 0
        for game in schedule:
            try:
                # Parse game date
                game_date = datetime.strptime(game['game_date'], '%Y-%m-%d').date()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO games (
                        game_pk, game_date, season, game_type, status,
                        home_team_id, away_team_id, home_score, away_score,
                        venue_name
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    game['game_id'],
                    game_date,
                    game.get('season', game_date.year),
                    game.get('game_type', 'R'),
                    game.get('status', 'Unknown'),
                    game['home_id'],
                    game['away_id'],
                    game.get('home_score', None),
                    game.get('away_score', None),
                    game.get('venue_name', '')
                ))
                inserted += 1
            except Exception as e:
                print(f"Error inserting game {game.get('game_id')}: {e}")
        
        conn.commit()
        conn.close()
        
        print(f"✅ Inserted {inserted} games")
        return inserted
    
    def collect_boxscore(self, game_pk):
        """Collect box score for a specific game"""
        try:
            # Get box score data
            boxscore = statsapi.boxscore_data(game_pk)
            
            if not boxscore:
                return 0
            
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            cursor = conn.cursor()
            
            # Get game_id from database
            game_id = cursor.execute(
                "SELECT game_id FROM games WHERE game_pk = ?", 
                (game_pk,)
            ).fetchone()
            
            if not game_id:
                print(f"  Game {game_pk} not found in database")
                conn.close()
                return 0
            
            game_id = game_id[0]
            
            inserted = 0
            
            # Get team IDs
            team_info = boxscore.get('teamInfo', {})
            away_team_id = team_info.get('away', {}).get('id')
            home_team_id = team_info.get('home', {}).get('id')
            
            # Process batting stats
            for team_key in ['away', 'home']:
                team_id = away_team_id if team_key == 'away' else home_team_id
                
                # Get batters list
                batters_key = f'{team_key}Batters'
                batters = boxscore.get(batters_key, [])
                
                for player_data in batters:
                    player_id = player_data.get('personId', 0)
                    if player_id == 0:  # Skip header rows
                        continue
                    
                    try:
                        # Parse numeric values (they come as strings)
                        def parse_int(val):
                            try:
                                return int(val) if val and val != '-' else 0
                            except:
                                return 0
                        
                        cursor.execute("""
                            INSERT OR REPLACE INTO box_scores_batting (
                                game_id, player_id, team_id,
                                at_bats, runs, hits, doubles, triples, home_runs,
                                rbi, walks, strikeouts, stolen_bases
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            game_id,
                            player_id,
                            team_id,
                            parse_int(player_data.get('ab')),
                            parse_int(player_data.get('r')),
                            parse_int(player_data.get('h')),
                            parse_int(player_data.get('doubles')),
                            parse_int(player_data.get('triples')),
                            parse_int(player_data.get('hr')),
                            parse_int(player_data.get('rbi')),
                            parse_int(player_data.get('bb')),
                            parse_int(player_data.get('k')),
                            parse_int(player_data.get('sb'))
                        ))
                        inserted += 1
                    except Exception as e:
                        continue
                
                # Process pitching stats
                pitchers_key = f'{team_key}Pitchers'
                pitchers = boxscore.get(pitchers_key, [])
                
                for player_data in pitchers:
                    player_id = player_data.get('personId', 0)
                    if player_id == 0:  # Skip header rows
                        continue
                    
                    try:
                        def parse_float(val):
                            try:
                                return float(val) if val and val != '-' else 0.0
                            except:
                                return 0.0
                        
                        def parse_int(val):
                            try:
                                return int(val) if val and val != '-' else 0
                            except:
                                return 0
                        
                        cursor.execute("""
                            INSERT OR REPLACE INTO box_scores_pitching (
                                game_id, player_id, team_id,
                                innings_pitched, hits_allowed, runs_allowed, earned_runs,
                                walks, strikeouts, home_runs_allowed
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            game_id,
                            player_id,
                            team_id,
                            parse_float(player_data.get('ip')),
                            parse_int(player_data.get('h')),
                            parse_int(player_data.get('r')),
                            parse_int(player_data.get('er')),
                            parse_int(player_data.get('bb')),
                            parse_int(player_data.get('k')),
                            parse_int(player_data.get('hr'))
                        ))
                        inserted += 1
                    except Exception as e:
                        continue
            
            conn.commit()
            conn.close()
            
            return inserted
            
        except Exception as e:
            print(f"  Error collecting boxscore for game {game_pk}: {e}")
            return 0
    
    def collect_games_with_boxscores(self, start_date, end_date):
        """Collect games and their box scores"""
        # First collect schedule
        self.collect_schedule(start_date, end_date)
        
        # Get games that need box scores
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        games = conn.execute("""
            SELECT game_pk, game_date, home_team_id, away_team_id, status
            FROM games
            WHERE game_date BETWEEN ? AND ?
            AND status IN ('Final', 'Completed')
            ORDER BY game_date
        """, (start_date, end_date)).fetchall()
        conn.close()
        
        print(f"\n{'='*70}")
        print(f" COLLECTING BOX SCORES FOR {len(games)} GAMES")
        print(f"{'='*70}\n")
        
        total_stats = 0
        for idx, (game_pk, game_date, home_id, away_id, status) in enumerate(games, 1):
            print(f"[{idx}/{len(games)}] Game {game_pk} ({game_date})...", end=' ')
            
            stats = self.collect_boxscore(game_pk)
            total_stats += stats
            
            print(f"{stats} stats")
            
            time.sleep(0.5)  # Rate limiting
        
        print(f"\n{'='*70}")
        print(f"✅ Collected {total_stats} player stats from {len(games)} games")
        print(f"{'='*70}")


def main():
    """Main data collection"""
    parser = argparse.ArgumentParser(description='Collect MLB data')
    parser.add_argument('--date', type=str, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--days', type=int, default=7, help='Number of days to collect')
    parser.add_argument('--season', type=int, help='Collect entire season (e.g., 2024)')
    parser.add_argument('--teams', action='store_true', help='Collect teams only')
    
    args = parser.parse_args()
    
    collector = MLBDataCollector()
    
    # Collect teams first
    if args.teams:
        collector.collect_teams()
        return
    
    # Collect teams if database is empty
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    team_count = conn.execute("SELECT COUNT(*) FROM teams").fetchone()[0]
    conn.close()
    
    if team_count == 0:
        collector.collect_teams()
    
    # Determine date range
    if args.season:
        # Full season: April 1 to October 31
        start_date = f"{args.season}-04-01"
        end_date = f"{args.season}-10-31"
    elif args.date:
        start = datetime.strptime(args.date, '%Y-%m-%d')
        end = start + timedelta(days=args.days - 1)
        start_date = start.strftime('%Y-%m-%d')
        end_date = end.strftime('%Y-%m-%d')
    else:
        # Default: last 7 days
        end = datetime.now()
        start = end - timedelta(days=6)
        start_date = start.strftime('%Y-%m-%d')
        end_date = end.strftime('%Y-%m-%d')
    
    # Collect data
    collector.collect_games_with_boxscores(start_date, end_date)


if __name__ == "__main__":
    main()
