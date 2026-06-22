# MLB Multi-Season Collection Status

## Collection Running

**Process**: Collecting 2021-2023 MLB seasons
**PID**: 60347
**Started**: November 20, 2025 @ 11:18 AM
**Logs**: 
- Main log: `/Users/jackholroyd/MLB_Stats/logs/multi_season_collection.log`
- Detail log: `/Users/jackholroyd/MLB_Stats/logs/mlb_collection.log`

## Seasons Being Collected

| Season | Games (approx) | Status |
|--------|---------------|--------|
| 2021   | ~2,900        | In Progress |
| 2022   | ~2,900        | Queued |
| 2023   | ~2,900        | Queued |
| 2024   | 2,857         | ✅ Already Complete |

**Total Expected**: ~11,500+ games (including 2024)

## Monitor Progress

```bash
# Watch main collection log
tail -f /Users/jackholroyd/MLB_Stats/logs/multi_season_collection.log

# Watch detailed progress
tail -f /Users/jackholroyd/MLB_Stats/logs/mlb_collection.log

# Check database counts
sqlite3 /Users/jackholroyd/MLB_Stats/data/mlb_data.db "
  SELECT season, COUNT(*) as games 
  FROM games 
  GROUP BY season 
  ORDER BY season;"

# Check process status
ps aux | grep collect_multiple_seasons.py | grep -v grep
```

## Estimated Timeline

- Rate: ~100-150 games/hour
- Per season: ~18-24 hours
- Total for 3 seasons: **~54-72 hours** (2-3 days)

## Files

- Collection script: `scripts/collect_multiple_seasons.py`
- Individual season collector: `scripts/get_all_games_stats.py`
- Database: `data/mlb_data.db` (currently 7.3 MB, will grow to ~30-40 MB)

## What You'll Have

Complete MLB data for 2021-2024 seasons:
- All regular season games
- Spring training games  
- Playoff games
- Complete batting stats per game
- Complete pitching stats per game
- Ready for historical analysis and ML models!
