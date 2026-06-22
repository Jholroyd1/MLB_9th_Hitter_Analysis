# MLB Stats Quick Reference

## Current Status

✅ **Database**: Initialized with schema (30 teams, 35 games, 141 player stats)
✅ **Dependencies**: MLB-StatsAPI, pandas, numpy installed
✅ **Data Collector**: Working - successfully tested with August 2024 games

## Common Commands

### Collect Recent Data
```bash
# Last 7 days
python scripts/collect_mlb_data.py

# Specific date range  
python scripts/collect_mlb_data.py --date 2024-08-01 --days 7

# Full season
python scripts/collect_mlb_data.py --season 2024
```

### Query Database
```bash
# Via Python
cd /Users/jackholroyd/MLB_Stats
.venv/bin/python -c "import sqlite3; conn = sqlite3.connect('data/mlb_data.db'); print(conn.execute('SELECT * FROM teams').fetchall())"

# Via SQLite CLI
sqlite3 data/mlb_data.db
```

### Example Queries

```sql
-- Top batters by hits
SELECT p.full_name, SUM(b.hits) as total_hits
FROM box_scores_batting b
JOIN players p ON b.player_id = p.player_id
GROUP BY b.player_id
ORDER BY total_hits DESC
LIMIT 10;

-- Top pitchers by strikeouts  
SELECT p.full_name, SUM(pi.strikeouts) as total_k
FROM box_scores_pitching pi
JOIN players p ON pi.player_id = p.player_id
GROUP BY pi.player_id
ORDER BY total_k DESC
LIMIT 10;

-- Games by team
SELECT t.team_name, COUNT(*) as games
FROM games g
JOIN teams t ON g.home_team_id = t.team_id OR g.away_team_id = t.team_id
GROUP BY t.team_id
ORDER BY games DESC;
```

## Database Schema

**Tables**:
- `teams` - All 30 MLB teams
- `games` - Game results, scores, venue  
- `box_scores_batting` - Batting stats by player/game
- `box_scores_pitching` - Pitching stats by player/game
- `players` - Player information (populated on first appearance)
- `play_by_play` - Game events (future)

## Next Steps

1. Collect full 2024 season data
2. Build player tracking system
3. Create visualization tools
4. Add predictive models (similar to NBA project)
