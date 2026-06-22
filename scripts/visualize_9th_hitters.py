import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set up the database path
DB_PATH = '../data/mlb_data.db'
OUTPUT_DIR = './data/visualizations'

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Set style for better-looking plots
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("Set2")

print("=" * 60)
print("9th Hitter Analysis - Visualization Script")
print("=" * 60)

# Connect to database
conn = sqlite3.connect(DB_PATH)

# Query 1: Team 9th hitter production by season
query = """
SELECT 
    t.team_name,
    g.season,
    COUNT(*) as games_batting_ninth,
    ROUND(SUM(bb.hits) * 1.0 / NULLIF(SUM(bb.at_bats), 0), 3) as avg_avg,
    ROUND((SUM(bb.hits) + SUM(bb.walks) + SUM(bb.hit_by_pitch)) * 1.0 / 
          NULLIF(SUM(bb.at_bats) + SUM(bb.walks) + SUM(bb.hit_by_pitch) + SUM(bb.sacrifice_flies), 0), 3) as avg_obp,
    ROUND((SUM(bb.hits) + SUM(bb.doubles) + 2*SUM(bb.triples) + 3*SUM(bb.home_runs)) * 1.0 / 
          NULLIF(SUM(bb.at_bats), 0), 3) as avg_slg,
    ROUND(
        ((SUM(bb.hits) + SUM(bb.walks) + SUM(bb.hit_by_pitch)) * 1.0 / 
         NULLIF(SUM(bb.at_bats) + SUM(bb.walks) + SUM(bb.hit_by_pitch) + SUM(bb.sacrifice_flies), 0)) +
        ((SUM(bb.hits) + SUM(bb.doubles) + 2*SUM(bb.triples) + 3*SUM(bb.home_runs)) * 1.0 / 
         NULLIF(SUM(bb.at_bats), 0)), 
    3) as avg_ops,
    ROUND(SUM(bb.rbi), 0) as total_rbi,
    ROUND(SUM(bb.runs), 0) as total_runs
FROM box_scores_batting bb
JOIN games g ON bb.game_id = g.game_id
LEFT JOIN teams t ON bb.team_id = t.team_id
WHERE bb.batting_order = 9
  AND bb.batting_order IS NOT NULL
  AND bb.at_bats > 0
GROUP BY t.team_name, g.season
HAVING games_batting_ninth >= 30
ORDER BY g.season DESC, avg_ops DESC;
"""

# Load data
df = pd.read_sql_query(query, conn)
conn.close()

print(f"\nLoaded {len(df)} team-season records")

# Get list of unique seasons
seasons = sorted(df['season'].unique(), reverse=True)
print(f"Seasons: {seasons}")

# ============================================================================
# Plot 1: Top 10 Teams by 9th Hitter OPS in 2026
# ============================================================================
print("\n📊 Creating Plot 1: Top 10 Teams by 9th Hitter OPS (2026)...")

df_2026 = df[df['season'] == 2026].head(10)

fig, ax = plt.subplots(figsize=(12, 8))
bars = ax.bar(df_2026['team_name'], df_2026['avg_ops'], color='steelblue', edgecolor='black')
ax.set_xlabel('Team', fontsize=12)
ax.set_ylabel('OPS', fontsize=12)
ax.set_title('Top 10 Teams by 9th Hitter OPS - 2026 Season', fontsize=16, fontweight='bold')
ax.set_ylim(0, 1.0)
ax.axhline(y=0.700, color='red', linestyle='--', alpha=0.7, label='League Average ~.700')
ax.legend()

# Add value labels on bars
for bar, ops in zip(bars, df_2026['avg_ops']):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
            f'{ops:.3f}', ha='center', va='bottom', fontsize=10)

plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/2026_top_10_teams_9th_ops.png', dpi=300, bbox_inches='tight')
plt.close()
print(f"  ✅ Saved: {OUTPUT_DIR}/2026_top_10_teams_9th_ops.png")

# ============================================================================
# Plot 2: Top Teams Over Time (Line Chart)
# ============================================================================
print("\n📊 Creating Plot 2: Top Teams 9th Hitter OPS Over Time...")

# Identify top 5 teams overall (by average OPS across seasons)
top_teams = df.groupby('team_name')['avg_ops'].mean().nlargest(8).index.tolist()
print(f"  Top teams: {top_teams}")

df_top = df[df['team_name'].isin(top_teams)]

fig, ax = plt.subplots(figsize=(14, 8))
for team in top_teams:
    team_data = df_top[df_top['team_name'] == team].sort_values('season')
    ax.plot(team_data['season'], team_data['avg_ops'], marker='o', linewidth=2, label=team)

ax.set_xlabel('Season', fontsize=12)
ax.set_ylabel('OPS', fontsize=12)
ax.set_title('9th Hitter OPS Over Time - Top Performing Teams', fontsize=16, fontweight='bold')
ax.set_ylim(0.4, 1.0)
ax.axhline(y=0.700, color='gray', linestyle='--', alpha=0.5, label='League Average ~.700')
ax.legend(loc='best', fontsize=9)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/top_teams_9th_ops_over_time.png', dpi=300, bbox_inches='tight')
plt.close()
print(f"  ✅ Saved: {OUTPUT_DIR}/top_teams_9th_ops_over_time.png")

# ============================================================================
# Plot 3: Heatmap - Teams vs Seasons (OPS)
# ============================================================================
print("\n📊 Creating Plot 3: Heatmap of 9th Hitter OPS by Team and Season...")

# Pivot the data for heatmap
pivot_df = df.pivot_table(index='team_name', columns='season', values='avg_ops')

fig, ax = plt.subplots(figsize=(14, 12))
im = ax.imshow(pivot_df.values, cmap='RdYlGn', aspect='auto', vmin=0.4, vmax=0.9)

# Set axis labels
ax.set_xticks(range(len(pivot_df.columns)))
ax.set_xticklabels(pivot_df.columns)
ax.set_yticks(range(len(pivot_df.index)))
ax.set_yticklabels(pivot_df.index, fontsize=8)

# Add colorbar
cbar = plt.colorbar(im, ax=ax)
cbar.set_label('OPS', fontsize=12)

ax.set_title('9th Hitter OPS by Team and Season', fontsize=16, fontweight='bold')
ax.set_xlabel('Season', fontsize=12)
ax.set_ylabel('Team', fontsize=12)

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/heatmap_9th_ops_by_team_season.png', dpi=300, bbox_inches='tight')
plt.close()
print(f"  ✅ Saved: {OUTPUT_DIR}/heatmap_9th_ops_by_team_season.png")

# ============================================================================
# Plot 4: 2022 Yankees - A Closer Look
# ============================================================================
print("\n📊 Creating Plot 4: 2022 Yankees 9th Hitter Performance...")

# Get the 2022 Yankees data
yankees_2022 = df[(df['team_name'] == 'New York Yankees') & (df['season'] == 2022)]

if not yankees_2022.empty:
    # Get comparison data (all teams in 2022)
    df_2022 = df[df['season'] == 2022].copy()
    
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Sort teams by OPS
    df_2022_sorted = df_2022.sort_values('avg_ops', ascending=True)
    colors = ['red' if team == 'New York Yankees' else 'steelblue' for team in df_2022_sorted['team_name']]
    
    bars = ax.barh(df_2022_sorted['team_name'], df_2022_sorted['avg_ops'], color=colors, edgecolor='black')
    
    ax.set_xlabel('OPS', fontsize=12)
    ax.set_ylabel('Team', fontsize=12)
    ax.set_title('2022 Season: 9th Hitter OPS by Team', fontsize=16, fontweight='bold')
    ax.axvline(x=0.700, color='gray', linestyle='--', alpha=0.5, label='League Average ~.700')
    ax.axvline(x=df_2022_sorted['avg_ops'].mean(), color='orange', linestyle='--', alpha=0.7, label='League Avg')
    ax.legend()
    
    # Highlight the Yankees' OPS
    yankees_ops = yankees_2022['avg_ops'].values[0]
    ax.text(yankees_ops + 0.01, 
            df_2022_sorted[df_2022_sorted['team_name'] == 'New York Yankees'].index[0],
            f'⭐ {yankees_ops:.3f}', 
            va='center', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/2022_teams_9th_ops.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✅ Saved: {OUTPUT_DIR}/2022_teams_9th_ops.png")

# ============================================================================
# Plot 5: Average 9th Hitter OPS by Season
# ============================================================================
print("\n📊 Creating Plot 5: Average 9th Hitter OPS by Season...")

season_avg = df.groupby('season')['avg_ops'].mean().reset_index()
season_avg.columns = ['season', 'avg_ops']

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(season_avg['season'], season_avg['avg_ops'], marker='o', linewidth=2, color='steelblue')
ax.set_xlabel('Season', fontsize=12)
ax.set_ylabel('Average OPS', fontsize=12)
ax.set_title('League Average 9th Hitter OPS by Season (2020-2026)', fontsize=16, fontweight='bold')
ax.set_ylim(0.5, 0.75)
ax.grid(True, alpha=0.3)

# Add value labels
for _, row in season_avg.iterrows():
    ax.annotate(f'{row["avg_ops"]:.3f}', 
                (row['season'], row['avg_ops']),
                textcoords="offset points", xytext=(0, 10),
                ha='center', fontsize=10)

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/season_avg_9th_ops_trend.png', dpi=300, bbox_inches='tight')
plt.close()
print(f"  ✅ Saved: {OUTPUT_DIR}/season_avg_9th_ops_trend.png")

# ============================================================================
# Summary Report
# ============================================================================
print("\n" + "=" * 60)
print("SUMMARY REPORT")
print("=" * 60)
print(f"\n📊 Generated {5} visualizations in: {OUTPUT_DIR}/")
print("\nFiles created:")
print("  1. 2026_top_10_teams_9th_ops.png - Top teams in 2026")
print("  2. top_teams_9th_ops_over_time.png - Top teams trend over years")
print("  3. heatmap_9th_ops_by_team_season.png - Heatmap of all teams/seasons")
print("  4. 2022_teams_9th_ops.png - 2022 season comparison")
print("  5. season_avg_9th_ops_trend.png - League average trend")

# Print some interesting stats
print("\n📈 Interesting Findings:")
best_overall = df.loc[df['avg_ops'].idxmax()]
print(f"  • Best single-season 9th hitter performance: {best_overall['team_name']} ({best_overall['season']}) with OPS = {best_overall['avg_ops']:.3f}")

worst_overall = df.loc[df['avg_ops'].idxmin()]
print(f"  • Worst single-season 9th hitter performance: {worst_overall['team_name']} ({worst_overall['season']}) with OPS = {worst_overall['avg_ops']:.3f}")

# Best team overall
best_team = df.groupby('team_name')['avg_ops'].mean().idxmax()
best_team_ops = df.groupby('team_name')['avg_ops'].mean().max()
print(f"  • Best team overall (average across seasons): {best_team} with OPS = {best_team_ops:.3f}")

print(f"\n✅ All visualizations saved to: {OUTPUT_DIR}/")