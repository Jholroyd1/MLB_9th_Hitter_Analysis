"""
Collect All MLB Games with Box Score Stats
Similar to NBA get_all_games_stats.py - comprehensive data collection
"""

import sqlite3
import statsapi
from datetime import datetime, timedelta
import time
import argparse
import logging


DB_PATH = "../data/mlb_data.db"


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('../logs/mlb_collection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class MLBStatsCollector:
    def collect_play_by_play(self, game_pk, game_id):
        """Collect and insert play-by-play data for a game, including batted ball data"""
        try:
            pbp = statsapi.get('game_playByPlay', {'gamePk': game_pk})
            all_plays = pbp.get('allPlays', [])
            if not all_plays:
                logger.warning(f"No play-by-play data for game {game_pk}")
                return 0
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            cursor = conn.cursor()
            inserted = 0
            for play in all_plays:
                event = play.get('result', {})
                matchup = play.get('matchup', {})
                pitch = play.get('pitchData', {})
                runners = play.get('runners', [])
                # Basic info
                inning = play.get('about', {}).get('inning')
                half_inning = play.get('about', {}).get('halfInning')
                at_bat_index = play.get('atBatIndex')
                pitch_number = play.get('playEndTime', None)  # Not always available
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

                cursor.execute('''
                    INSERT INTO play_by_play (
                        game_id, play_id, inning, half_inning, at_bat_index, pitch_number,
                        event_type, event_description, result_type, batter_id, pitcher_id,
                        runner_on_first_id, runner_on_second_id, runner_on_third_id,
                        outs, balls, strikes, count, pitch_type, pitch_speed, runs_scored, rbi,
                        launch_speed, launch_angle, total_distance, trajectory, hardness, location, coord_x, coord_y
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
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
                    coord_y
                ))
                inserted += 1
            conn.commit()
            conn.close()
            logger.info(f"Inserted {inserted} play-by-play events for game {game_pk}")
            return inserted
        except Exception as e:
            logger.error(f"Error collecting play-by-play for game {game_pk}: {e}")
            return 0
    """Comprehensive MLB stats collector"""
    
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.stats_collected = 0
        self.games_processed = 0
        self.errors = 0
        
    def collect_boxscore(self, game_pk, game_date, home_team, away_team):
        """Collect box score for a specific game"""
        try:
            # Get box score data
            boxscore = statsapi.boxscore_data(game_pk)
            
            if not boxscore:
                logger.warning(f"No boxscore data for game {game_pk}")
                return 0
            
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            cursor = conn.cursor()
            
            # Get game_id from database
            game_id_result = cursor.execute(
                "SELECT game_id FROM games WHERE game_pk = ?", 
                (game_pk,)
            ).fetchone()
            
            if not game_id_result:
                logger.warning(f"Game {game_pk} not found in database")
                conn.close()
                return 0
            
            game_id = game_id_result[0]
            
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

                    # Insert/update player info
                    full_name = player_data.get('name', '')
                    first_name = full_name.split(' ')[0] if full_name else ''
                    last_name = ' '.join(full_name.split(' ')[1:]) if full_name else ''
                    position = player_data.get('position', '')
                    bat_side = player_data.get('batSide', '')
                    pitch_hand = player_data.get('pitchHand', '')
                    cursor.execute("""
                        INSERT OR IGNORE INTO players (
                            player_id, full_name, first_name, last_name, position, bat_side, pitch_hand
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        player_id,
                        full_name,
                        first_name,
                        last_name,
                        position,
                        bat_side,
                        pitch_hand
                    ))

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
                        logger.debug(f"Error inserting batter {player_id}: {e}")
                        continue
                
                # Process pitching stats
                pitchers_key = f'{team_key}Pitchers'
                pitchers = boxscore.get(pitchers_key, [])
                
                for player_data in pitchers:
                    player_id = player_data.get('personId', 0)
                    if player_id == 0:  # Skip header rows
                        continue

                    # Insert/update player info
                    full_name = player_data.get('name', '')
                    first_name = full_name.split(' ')[0] if full_name else ''
                    last_name = ' '.join(full_name.split(' ')[1:]) if full_name else ''
                    position = player_data.get('position', '')
                    bat_side = player_data.get('batSide', '')
                    pitch_hand = player_data.get('pitchHand', '')
                    cursor.execute("""
                        INSERT OR IGNORE INTO players (
                            player_id, full_name, first_name, last_name, position, bat_side, pitch_hand
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        player_id,
                        full_name,
                        first_name,
                        last_name,
                        position,
                        bat_side,
                        pitch_hand
                    ))

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
                        logger.debug(f"Error inserting pitcher {player_id}: {e}")
                        continue
            
            conn.commit()
            conn.close()
            
            return inserted
            
        except Exception as e:
            logger.error(f"Error collecting boxscore for game {game_pk}: {e}")
            self.errors += 1
            return 0
    
    def collect_season_schedule(self, season, team_id=None):
        """Collect all games for a season in monthly chunks"""
        logger.info(f"Collecting schedule for {season} season...")
        
        # MLB season: March (spring) to November (World Series)
        # Collect in monthly chunks to avoid API timeouts
        months = [
            (f"{season}-03-01", f"{season}-03-31"),  # Spring training
            (f"{season}-04-01", f"{season}-04-30"),  # April
            (f"{season}-05-01", f"{season}-05-31"),  # May
            (f"{season}-06-01", f"{season}-06-30"),  # June
            (f"{season}-07-01", f"{season}-07-31"),  # July
            (f"{season}-08-01", f"{season}-08-31"),  # August
            (f"{season}-09-01", f"{season}-09-30"),  # September
            (f"{season}-10-01", f"{season}-10-31"),  # October (playoffs)
            (f"{season}-11-01", f"{season}-11-15"),  # November (World Series)
        ]
        
        all_schedule = []
        for start_date, end_date in months:
            try:
                if team_id:
                    schedule = statsapi.schedule(
                        start_date=start_date, 
                        end_date=end_date,
                        team=team_id
                    )
                else:
                    schedule = statsapi.schedule(
                        start_date=start_date, 
                        end_date=end_date
                    )
                all_schedule.extend(schedule)
                logger.info(f"  {start_date} to {end_date}: {len(schedule)} games")
                time.sleep(1)  # Rate limiting
            except Exception as e:
                logger.warning(f"Error fetching {start_date} to {end_date}: {e}")
                continue
        
        schedule = all_schedule
        
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
                logger.error(f"Error inserting game {game.get('game_id')}: {e}")
        
        conn.commit()
        conn.close()
        
        logger.info(f"Inserted {inserted} games for {season} season")
        return inserted
    
    def collect_season_stats(self, season, resume_from_game=None):
        """Collect all stats for a season"""
        logger.info(f"="*70)
        logger.info(f"COLLECTING ALL STATS FOR {season} SEASON")
        logger.info(f"="*70)
        
        # First collect schedule
        self.collect_season_schedule(season)
        
        # Get all completed games for the season
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        
        # Build query with optional resume point
        query = """
            SELECT game_pk, game_date, home_team_id, away_team_id, status, game_id
            FROM games
            WHERE season = ?
            AND status IN ('Final', 'Completed', 'Game Over')
            AND game_type = 'R'
        """
        
        if resume_from_game:
            query += f" AND game_pk >= {resume_from_game}"
        
        query += " ORDER BY game_date, game_pk"
        
        games = conn.execute(query, (season,)).fetchall()
        conn.close()
        
        logger.info(f"\nFound {len(games)} completed games to process")
        
        if resume_from_game:
            logger.info(f"Resuming from game_pk {resume_from_game}")
        
        start_time = time.time()
        
        for idx, (game_pk, game_date, home_id, away_id, status, game_id) in enumerate(games, 1):
            # Check if we already have stats for this game
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            existing_stats = conn.execute(
                "SELECT COUNT(*) FROM box_scores_batting WHERE game_id = ?",
                (game_id,)
            ).fetchone()[0]
            conn.close()
            
            if existing_stats > 0 and not resume_from_game:
                logger.info(f"[{idx}/{len(games)}] Game {game_pk} ({game_date}) - Already has stats, skipping")
                self.games_processed += 1
                continue
            
            stats = self.collect_boxscore(game_pk, game_date, home_id, away_id)
            self.collect_play_by_play(game_pk, game_id)
            self.stats_collected += stats
            self.games_processed += 1
            logger.info(f"[{idx}/{len(games)}] Game {game_pk} ({game_date}) - {stats} stats + play-by-play")
            
            # Progress report every 50 games
            if idx % 50 == 0:
                elapsed = time.time() - start_time
                rate = idx / elapsed * 3600  # games per hour
                remaining = len(games) - idx
                eta_hours = remaining / rate if rate > 0 else 0
                
                logger.info(f"\n{'='*70}")
                logger.info(f"Progress: {idx}/{len(games)} ({idx/len(games)*100:.1f}%)")
                logger.info(f"Stats collected: {self.stats_collected:,}")
                logger.info(f"Rate: {rate:.1f} games/hour")
                logger.info(f"ETA: {eta_hours:.1f} hours")
                logger.info(f"Errors: {self.errors}")
                logger.info(f"{'='*70}\n")
            
            # Rate limiting
            time.sleep(0.6)
        
        # Final summary
        elapsed = time.time() - start_time
        logger.info(f"\n{'='*70}")
        logger.info(f"COLLECTION COMPLETE - {season} Season")
        logger.info(f"{'='*70}")
        logger.info(f"Games processed: {self.games_processed:,}")
        logger.info(f"Stats collected: {self.stats_collected:,}")
        logger.info(f"Errors: {self.errors}")
        logger.info(f"Time elapsed: {elapsed/3600:.2f} hours")
        logger.info(f"Average rate: {self.games_processed/elapsed*3600:.1f} games/hour")
        logger.info(f"{'='*70}")


def main():
    """Main collection entry point"""
    parser = argparse.ArgumentParser(description='Collect all MLB games and stats')
    parser.add_argument('--season', type=int, required=True, help='Season year (e.g., 2024)')
    parser.add_argument('--resume', type=int, help='Resume from game_pk')
    parser.add_argument('--game_id', type=int, help='Collect only this game_id (for backfill)')

    args = parser.parse_args()

    # Create logs directory if it doesn't exist
    import os
    os.makedirs('../logs', exist_ok=True)

    # Initialize collector
    collector = MLBStatsCollector()

    # Collect teams first if needed
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    team_count = conn.execute("SELECT COUNT(*) FROM teams").fetchone()[0]
    conn.close()

    if team_count == 0:
        logger.info("No teams found, collecting teams first...")
        from collect_mlb_data import MLBDataCollector
        team_collector = MLBDataCollector()
        team_collector.collect_teams()

    if args.game_id:
        # Backfill only the specified game_id
        conn = sqlite3.connect(DB_PATH, timeout=30.0)
        row = conn.execute("SELECT game_pk, game_date, home_team_id, away_team_id, status, game_id FROM games WHERE game_id = ?", (args.game_id,)).fetchone()
        conn.close()
        if not row:
            logger.error(f"Game_id {args.game_id} not found in database.")
            return
        game_pk, game_date, home_id, away_id, status, game_id = row
        logger.info(f"Backfilling single game: {args.game_id} (pk={game_pk}, date={game_date})")
        stats = collector.collect_boxscore(game_pk, game_date, home_id, away_id)
        collector.collect_play_by_play(game_pk, game_id)
        logger.info(f"Backfill complete for game_id {args.game_id}")
    else:
        # Collect season stats as before
        collector.collect_season_stats(args.season, resume_from_game=args.resume)


if __name__ == "__main__":
    main()
