"""
Collect MLB data for multiple seasons (2021-2023)
"""

import subprocess
import sys
import time
from datetime import datetime

def run_season_collection(season):
    """Run collection for a single season"""
    print(f"\n{'='*80}")
    print(f"Starting collection for {season} season")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")
    
    start_time = time.time()
    
    # Run the collection script
    cmd = [sys.executable, 'get_all_games_stats.py', '--season', str(season)]
    result = subprocess.run(cmd, cwd='/Users/jackholroyd/MLB_Stats/scripts')
    
    elapsed = time.time() - start_time
    
    print(f"\n{'='*80}")
    print(f"Completed {season} season in {elapsed/3600:.2f} hours")
    print(f"Exit code: {result.returncode}")
    print(f"{'='*80}\n")
    
    return result.returncode == 0

def main():
    """Collect 2021-2023 seasons (2024 already done)"""
    seasons = [2021, 2022, 2023]
    
    print(f"{'='*80}")
    print(f"MLB Multi-Season Data Collection")
    print(f"Seasons to collect: {seasons}")
    print(f"Note: 2024 season already collected (2,857 games)")
    print(f"{'='*80}\n")
    
    overall_start = time.time()
    results = {}
    
    for season in seasons:
        success = run_season_collection(season)
        results[season] = "SUCCESS" if success else "FAILED"
        
        if not success:
            print(f"WARNING: {season} collection failed, continuing to next season...")
    
    # Final summary
    overall_elapsed = time.time() - overall_start
    
    print(f"\n\n{'='*80}")
    print(f"MULTI-SEASON COLLECTION COMPLETE")
    print(f"{'='*80}")
    print(f"Total time: {overall_elapsed/3600:.2f} hours")
    print(f"\nResults:")
    for season, result in results.items():
        print(f"  {season}: {result}")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    main()
