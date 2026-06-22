import argparse
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import sys
from datetime import datetime

DB_PATH = 'data/mlb_data.db'

# --- Field geometry (simple MLB field) ---
def draw_field(ax):
    home_plate = np.array([0, 0])
    first_base = np.array([90, 0])
    second_base = np.array([90, 90])
    third_base = np.array([0, 90])
    mound = np.array([60.5, 0])
    # Outfield fence: 400ft to center, 330ft to corners
    fence_points = []
    for angle in np.linspace(45, 135, 200):
        rad = np.deg2rad(angle)
        dist = 330 + (400-330)*np.cos(np.deg2rad(angle-90))
        x = dist * np.cos(rad)
        y = dist * np.sin(rad)
        fence_points.append([x, y])
    fence_points = np.array(fence_points)
    # Outfield grass
    outfield_poly = plt.Polygon(fence_points, closed=True, color='#cbe7ea', zorder=1)
    ax.add_patch(outfield_poly)
    # Basepaths
    ax.plot([home_plate[0], first_base[0], second_base[0], third_base[0], home_plate[0]],
            [home_plate[1], first_base[1], second_base[1], third_base[1], home_plate[1]], color='gray', lw=2)
    # Bases
    base_size = 5
    for base in [home_plate, first_base, second_base, third_base]:
        ax.add_patch(patches.Rectangle(base - base_size/2, base_size, base_size, color='white', ec='black', zorder=10))
    # Mound
    mound_radius = 9
    ax.add_patch(patches.Circle(mound, mound_radius, edgecolor='gray', facecolor='#e6d3b3', lw=1, alpha=0.7, zorder=5))
    # Outfield fence
    ax.plot(fence_points[:,0], fence_points[:,1], color='#b2c7c7', lw=2, zorder=6)
    # Foul lines
    ax.plot([home_plate[0], fence_points[0,0]], [home_plate[1], fence_points[0,1]], color='#b2c7c7', lw=2, zorder=7)
    ax.plot([home_plate[0], fence_points[-1,0]], [home_plate[1], fence_points[-1,1]], color='#b2c7c7', lw=2, zorder=7)
    # Fence distance labels
    ax.text(fence_points[0,0], fence_points[0,1]-15, '330', color='#b2c7c7', fontsize=12, ha='center', va='center', fontweight='bold')
    ax.text(fence_points[-1,0], fence_points[-1,1]-15, '330', color='#b2c7c7', fontsize=12, ha='center', va='center', fontweight='bold')
    ax.text(0, 410, '410', color='#b2c7c7', fontsize=12, ha='center', va='center', fontweight='bold')
    ax.set_xlim(-50, 450-125)
    ax.set_ylim(-50, 450)
    ax.set_aspect('equal', adjustable='box')
    ax.axis('off')

def get_player_id(conn, player_name):
    # Try exact match, then fallback to LIKE
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
    sys.exit(1)

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

def main():
    parser = argparse.ArgumentParser(description="Create a spray chart for any player and date range.")
    parser.add_argument('--player', required=True, help='Player full name (case-insensitive)')
    parser.add_argument('--start', required=True, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', required=True, help='End date (YYYY-MM-DD)')
    parser.add_argument('--output', default=None, help='Output PNG file (optional)')
    args = parser.parse_args()

    # Validate dates
    try:
        datetime.strptime(args.start, '%Y-%m-%d')
        datetime.strptime(args.end, '%Y-%m-%d')
    except ValueError:
        print('Invalid date format. Use YYYY-MM-DD.')
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    player_id, player_name = get_player_id(conn, args.player)
    df = query_batted_balls(conn, player_id, args.start, args.end)
    conn.close()

    if df.empty:
        print(f"No batted ball data found for {player_name} between {args.start} and {args.end}.")
        sys.exit(0)

    fig, ax = plt.subplots(figsize=(7, 7))
    draw_field(ax)
    ax.scatter(df['coord_x'], df['coord_y'], alpha=0.85, c='#e6550d', edgecolors='white', linewidths=1.5, s=60, zorder=20)
    ax.set_title(f"Spray Chart: {player_name}\n{args.start} to {args.end}", fontsize=14)
    plt.tight_layout()
    if args.output:
        plt.savefig(args.output, dpi=300, bbox_inches='tight', pad_inches=0.05)
        print(f"Spray chart saved to {args.output}")
    else:
        plt.show()

if __name__ == '__main__':
    main()
