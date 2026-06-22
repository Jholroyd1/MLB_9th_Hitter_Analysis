import numpy as np
import sqlite3
import plotly.graph_objects as go
import argparse
import pandas as pd
from datetime import datetime

DB_PATH = 'data/mlb_data.db'

# --- Draw a baseball field with specified base coordinates using Plotly ---
def get_field_shapes():
    home = (0, 0)
    first = (63, 63)
    second = (0, 126)
    third = (-63, 63)
    y_shift = 0 - home[1]
    home = (home[0], home[1] + y_shift)
    first = (first[0], first[1] + y_shift)
    second = (second[0], second[1] + y_shift)
    third = (third[0], third[1] + y_shift)
    diamond_x = [home[0], first[0], second[0], third[0], home[0]]
    diamond_y = [home[1], first[1], second[1], third[1], home[1]]
    fence_angles = np.linspace(-45, 45, 200)
    fence_x = []
    fence_y = []
    for angle in fence_angles:
        rad = np.deg2rad(angle)
        radius = 330 + (400 - 330) * np.cos(np.deg2rad(angle))
        fence_x.append(radius * np.sin(rad))
        fence_y.append(radius * np.cos(rad) + y_shift)
    foul_left_x = [third[0], fence_x[0]]
    foul_left_y = [third[1], fence_y[0]]
    foul_right_x = [first[0], fence_x[-1]]
    foul_right_y = [first[1], fence_y[-1]]
    return diamond_x, diamond_y, fence_x, fence_y, foul_left_x, foul_left_y, foul_right_x, foul_right_y, y_shift

def get_player_id(conn, player_name):
    cur = conn.cursor()
    cur.execute("SELECT player_id, full_name FROM players WHERE full_name = ? COLLATE NOCASE", (player_name,))
    row = cur.fetchone()
    if row:
        return row[0], row[1]
    cur.execute("SELECT player_id, full_name FROM players WHERE full_name LIKE ? COLLATE NOCASE", (f"%{player_name}%",))
    row = cur.fetchone()
    if row:
        return row[0], row[1]
    print(f"Player '{player_name}' not found in database.")
    exit(1)

def query_batted_balls(conn, player_id, start_date, end_date):
    sql = '''
    SELECT pbp.coord_x, pbp.coord_y, pbp.event_type, g.game_date
    FROM play_by_play pbp
    JOIN games g ON pbp.game_id = g.game_id
    WHERE pbp.batter_id = ?
      AND pbp.coord_x IS NOT NULL AND pbp.coord_y IS NOT NULL
      AND g.game_date BETWEEN ? AND ?
    '''
    df = pd.read_sql_query(sql, conn, params=(player_id, start_date, end_date))
    return df

def statcast_transform(hc_x, hc_y):
    # Statcast to field transformation (same as original script)
    x = 2.5 * (hc_x - 125.42)
    y = 2.5 * (198.27 - hc_y)
    return x, y

def main():
    parser = argparse.ArgumentParser(description="Create an interactive spray chart for any player and date range.")
    parser.add_argument('--player', required=True, help='Player full name (case-insensitive)')
    parser.add_argument('--start', required=True, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', required=True, help='End date (YYYY-MM-DD)')
    parser.add_argument('--output', default=None, help='Output HTML file (optional)')
    parser.add_argument('--outcome', default=None, help='Filter by batted ball outcome/event type (e.g., Home Run, Single, Out, etc.)')
    args = parser.parse_args()

    try:
        datetime.strptime(args.start, '%Y-%m-%d')
        datetime.strptime(args.end, '%Y-%m-%d')
    except ValueError:
        print('Invalid date format. Use YYYY-MM-DD.')
        exit(1)

    conn = sqlite3.connect(DB_PATH)
    player_id, player_name = get_player_id(conn, args.player)
    df = query_batted_balls(conn, player_id, args.start, args.end)
    if args.outcome:
        df = df[df['event_type'].str.lower() == args.outcome.strip().lower()]
    conn.close()

    if df.empty:
        print(f"No batted ball data found for {player_name} between {args.start} and {args.end}.")
        exit(0)

    # Transform Statcast coordinates
    statcast_x = []
    statcast_y = []
    event_types = []
    distances = []
    for _, row in df.iterrows():
        hc_x = row['coord_x']
        hc_y = row['coord_y']
        event_type = row['event_type']
        x, y = statcast_transform(hc_x, hc_y)
        statcast_x.append(x)
        statcast_y.append(y)
        event_types.append(event_type)
        distances.append(np.sqrt(x**2 + y**2))

    color_map = {
        'home_run': 'red',
        'single': 'green',
        'double': 'blue',
        'triple': 'purple',
    }
    colors = []
    for etype in event_types:
        if etype in color_map:
            colors.append(color_map[etype])
        elif 'out' in etype:
            colors.append('gray')
        else:
            colors.append('black')

    diamond_x, diamond_y, fence_x, fence_y, foul_left_x, foul_left_y, foul_right_x, foul_right_y, y_shift = get_field_shapes()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=diamond_x, y=diamond_y, mode='lines', line=dict(color='black', width=2), showlegend=False))
    fig.add_trace(go.Scatter(x=fence_x, y=fence_y, mode='lines', line=dict(color='black', width=2), showlegend=False))
    fig.add_trace(go.Scatter(x=foul_left_x, y=foul_left_y, mode='lines', line=dict(color='black', width=2), showlegend=False))
    fig.add_trace(go.Scatter(x=foul_right_x, y=foul_right_y, mode='lines', line=dict(color='black', width=2), showlegend=False))

    hover_text = [f"Event: {etype}<br>x: {x:.1f} ft<br>y: {y:.1f} ft<br>Distance: {d:.1f} ft" for etype, x, y, d in zip(event_types, statcast_x, statcast_y, distances)]
    fig.add_trace(go.Scatter(
        x=statcast_x, y=statcast_y, mode='markers',
        marker=dict(color=colors, size=8, line=dict(width=1, color='black')),
        text=hover_text, hoverinfo='text', name='Batted Balls'))

    margin_x = (max(statcast_x) - min(statcast_x)) * 0.1 if statcast_x else 50
    margin_y = (max(statcast_y) - min(statcast_y)) * 0.1 if statcast_y else 50
    xmin = min(-350, min(statcast_x) - margin_x)
    xmax = max(350, max(statcast_x) + margin_x)
    ymin = min(-20 + y_shift, min(statcast_y) - margin_y)
    ymax = max(450 + y_shift, max(statcast_y) + margin_y)
    fig.update_layout(
        title=f'Spray Chart: {player_name} {args.start} to {args.end}',
        xaxis=dict(title='Feet (x)', range=[xmin, xmax], scaleanchor='y', scaleratio=1),
        yaxis=dict(title='Feet (y)', range=[ymin, ymax]),
        width=900, height=900,
        showlegend=False
    )

    output_path = args.output or f"data/{player_name.replace(' ', '_').lower()}_spray_chart_{args.start}_to_{args.end}.html"
    fig.write_html(output_path)
    print(f'Interactive plot saved as {output_path}')

if __name__ == '__main__':
    main()
