-- MLB Stats Database Schema

-- Teams
CREATE TABLE IF NOT EXISTS teams (
    team_id INTEGER PRIMARY KEY,
    team_name TEXT NOT NULL,
    team_abbr TEXT,
    division TEXT,
    league TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Players
CREATE TABLE IF NOT EXISTS players (
    player_id INTEGER PRIMARY KEY,
    full_name TEXT NOT NULL,
    first_name TEXT,
    last_name TEXT,
    position TEXT,
    bat_side TEXT,  -- L, R, S (switch)
    pitch_hand TEXT,  -- L, R
    current_team_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (current_team_id) REFERENCES teams(team_id)
);

-- Games
CREATE TABLE IF NOT EXISTS games (
    game_id INTEGER PRIMARY KEY,
    game_pk INTEGER UNIQUE,  -- MLB's primary key
    game_date DATE NOT NULL,
    game_datetime TIMESTAMP,
    season INTEGER NOT NULL,
    game_type TEXT,  -- R (Regular), P (Playoffs), S (Spring), etc.
    status TEXT,
    home_team_id INTEGER NOT NULL,
    away_team_id INTEGER NOT NULL,
    home_score INTEGER,
    away_score INTEGER,
    venue_name TEXT,
    venue_id INTEGER,
    weather_condition TEXT,
    weather_temp INTEGER,
    wind TEXT,
    attendance INTEGER,
    game_duration_minutes INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (home_team_id) REFERENCES teams(team_id),
    FOREIGN KEY (away_team_id) REFERENCES teams(team_id)
);

-- Box Scores - Batting
CREATE TABLE IF NOT EXISTS box_scores_batting (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id INTEGER NOT NULL,
    player_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    batting_order INTEGER,
    position TEXT,
    -- Batting stats
    at_bats INTEGER DEFAULT 0,
    runs INTEGER DEFAULT 0,
    hits INTEGER DEFAULT 0,
    doubles INTEGER DEFAULT 0,
    triples INTEGER DEFAULT 0,
    home_runs INTEGER DEFAULT 0,
    rbi INTEGER DEFAULT 0,
    walks INTEGER DEFAULT 0,
    strikeouts INTEGER DEFAULT 0,
    stolen_bases INTEGER DEFAULT 0,
    caught_stealing INTEGER DEFAULT 0,
    hit_by_pitch INTEGER DEFAULT 0,
    sacrifice_hits INTEGER DEFAULT 0,
    sacrifice_flies INTEGER DEFAULT 0,
    left_on_base INTEGER DEFAULT 0,
    -- Advanced
    batting_avg REAL,
    obp REAL,  -- On-base percentage
    slg REAL,  -- Slugging percentage
    ops REAL,  -- On-base + slugging
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (game_id) REFERENCES games(game_id),
    FOREIGN KEY (player_id) REFERENCES players(player_id),
    FOREIGN KEY (team_id) REFERENCES teams(team_id),
    UNIQUE(game_id, player_id)
);

-- Box Scores - Pitching
CREATE TABLE IF NOT EXISTS box_scores_pitching (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id INTEGER NOT NULL,
    player_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    -- Pitching stats
    innings_pitched REAL,
    hits_allowed INTEGER DEFAULT 0,
    runs_allowed INTEGER DEFAULT 0,
    earned_runs INTEGER DEFAULT 0,
    walks INTEGER DEFAULT 0,
    strikeouts INTEGER DEFAULT 0,
    home_runs_allowed INTEGER DEFAULT 0,
    hit_batsmen INTEGER DEFAULT 0,
    pitches_thrown INTEGER DEFAULT 0,
    strikes INTEGER DEFAULT 0,
    balls INTEGER DEFAULT 0,
    -- Game outcome
    win BOOLEAN DEFAULT 0,
    loss BOOLEAN DEFAULT 0,
    save BOOLEAN DEFAULT 0,
    hold BOOLEAN DEFAULT 0,
    blown_save BOOLEAN DEFAULT 0,
    -- Advanced
    era REAL,  -- Earned run average
    whip REAL,  -- Walks + hits per inning pitched
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (game_id) REFERENCES games(game_id),
    FOREIGN KEY (player_id) REFERENCES players(player_id),
    FOREIGN KEY (team_id) REFERENCES teams(team_id),
    UNIQUE(game_id, player_id)
);

-- Play by Play
CREATE TABLE IF NOT EXISTS play_by_play (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id INTEGER NOT NULL,
    play_id TEXT,
    inning INTEGER,
    half_inning TEXT,  -- top, bottom
    at_bat_index INTEGER,
    pitch_number INTEGER,
    -- Event
    event_type TEXT,
    event_description TEXT,
    result_type TEXT,  -- single, double, strikeout, walk, etc.
    -- Players involved
    batter_id INTEGER,
    pitcher_id INTEGER,
    runner_on_first_id INTEGER,
    runner_on_second_id INTEGER,
    runner_on_third_id INTEGER,
    -- Game state
    outs INTEGER,
    balls INTEGER,
    strikes INTEGER,
    count TEXT,
    -- Pitch data (if available)
    pitch_type TEXT,
    pitch_speed REAL,
    -- Outcome
    runs_scored INTEGER DEFAULT 0,
    rbi INTEGER DEFAULT 0,
    -- Batted ball data (hitData)
    launch_speed REAL,
    launch_angle REAL,
    total_distance REAL,
    trajectory TEXT,
    hardness TEXT,
    location TEXT,
    coord_x REAL,
    coord_y REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (game_id) REFERENCES games(game_id),
    FOREIGN KEY (batter_id) REFERENCES players(player_id),
    FOREIGN KEY (pitcher_id) REFERENCES players(player_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_games_date ON games(game_date);
CREATE INDEX IF NOT EXISTS idx_games_season ON games(season);
CREATE INDEX IF NOT EXISTS idx_games_teams ON games(home_team_id, away_team_id);
CREATE INDEX IF NOT EXISTS idx_batting_game ON box_scores_batting(game_id);
CREATE INDEX IF NOT EXISTS idx_batting_player ON box_scores_batting(player_id);
CREATE INDEX IF NOT EXISTS idx_pitching_game ON box_scores_pitching(game_id);
CREATE INDEX IF NOT EXISTS idx_pitching_player ON box_scores_pitching(player_id);
CREATE INDEX IF NOT EXISTS idx_pbp_game ON play_by_play(game_id);
