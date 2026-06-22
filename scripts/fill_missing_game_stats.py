import sqlite3
import statsapi
import time
import logging

DB_PATH = 'data/mlb_data.db'
LOG_PATH = 'logs/fill_missing_game_stats.log'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_PATH),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Get all non-spring games missing batting stats
cursor.execute("""
SELECT game_id, game_pk, season FROM games 
WHERE game_id NOT IN (SELECT DISTINCT game_id FROM box_scores_batting) 
AND game_type != 'S'
ORDER BY season, game_date
""")
games = cursor.fetchall()
logger.info(f"Found {len(games)} games missing stats.")

from get_all_games_stats import MLBStatsCollector
collector = MLBStatsCollector(db_path=DB_PATH)

for idx, (game_id, game_pk, season) in enumerate(games, 1):
    logger.info(f"[{idx}/{len(games)}] Filling stats for game_pk={game_pk}, season={season}")
    # Get game info
    cursor.execute("SELECT game_date, home_team_id, away_team_id FROM games WHERE game_id=?", (game_id,))
    row = cursor.fetchone()
    if not row:
        logger.warning(f"Game {game_id} not found in DB.")
        continue
    game_date, home_team_id, away_team_id = row
    try:
        collector.collect_boxscore(game_pk, game_date, home_team_id, away_team_id)
        time.sleep(0.6)  # Respect API rate limit
    except Exception as e:
        logger.error(f"Error collecting boxscore for game_pk={game_pk}: {e}")

conn.close()
logger.info("Done filling missing game stats.")
