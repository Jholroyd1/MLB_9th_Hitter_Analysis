#!/usr/bin/env python3
"""
Attempt to scrape Baseball Savant for missing batted ball coordinates.
For each event in missing_batted_ball_coords.csv, try to find the play on Baseball Savant and extract coordinates if available.
This script is experimental and may be rate-limited or blocked by site changes.
"""
import csv
import time
import requests
from bs4 import BeautifulSoup

CSV_PATH = '../data/missing_batted_ball_coords.csv'
OUTPUT_PATH = '../data/savant_scraped_coords.csv'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (compatible; MLBStatsBot/1.0)'
}

# Helper to build a Baseball Savant search URL for a given game and batter
# Note: Savant URLs are not directly by game_id, so we use batter, event, and year for best effort

def search_savant_url(batter_id, year):
    # Example: https://baseballsavant.mlb.com/savant-player/juan-soto-665742?stats=statcast-r-hitting-mlb
    return f"https://baseballsavant.mlb.com/savant-player/{batter_id}?stats=statcast-r-hitting-mlb&season={year}"

def main():
    with open(CSV_PATH) as infile, open(OUTPUT_PATH, 'w', newline='') as outfile:
        reader = csv.reader(infile, delimiter='|')
        writer = csv.writer(outfile)
        writer.writerow(['game_id', 'at_bat_index', 'event_type', 'batter_id', 'pitcher_id', 'event_description', 'coord_x', 'coord_y', 'savant_url'])
        for row in reader:
            game_id, at_bat_index, event_type, batter_id, pitcher_id, event_description = row
            # Try to infer year from game_id (first 2 digits after 2000, e.g. 26603 likely 2021)
            try:
                year = 2000 + int(str(game_id)[:2])
            except Exception:
                year = ''
            url = search_savant_url(batter_id, year)
            print(f"Scraping {url} for game {game_id}, at_bat_index {at_bat_index}")
            try:
                resp = requests.get(url, headers=HEADERS, timeout=10)
                if resp.status_code != 200:
                    print(f"Failed to fetch {url} (status {resp.status_code})")
                    writer.writerow([game_id, at_bat_index, event_type, batter_id, pitcher_id, event_description, '', '', url])
                    continue
                soup = BeautifulSoup(resp.text, 'html.parser')
                # This is a placeholder: Savant's page structure is complex and may require manual inspection
                # Look for statcast tables or batted ball charts
                # For now, just record that we visited the page
                # TODO: Implement more precise scraping if possible
                writer.writerow([game_id, at_bat_index, event_type, batter_id, pitcher_id, event_description, '', '', url])
            except Exception as e:
                print(f"Error scraping {url}: {e}")
                writer.writerow([game_id, at_bat_index, event_type, batter_id, pitcher_id, event_description, '', '', url])
            time.sleep(1.5)  # Be polite to the server

if __name__ == "__main__":
    main()
