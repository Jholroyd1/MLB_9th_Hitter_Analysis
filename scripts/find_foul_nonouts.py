import numpy as np
import csv

# Foul territory check: returns True if point is outside the lines from home to 1st/3rd base to outfield fence
# We'll use the same transformation as the plot

def is_foul(x, y):
    # Foul lines: from home (0,0) to fence_x[0], fence_y[0] (left) and fence_x[-1], fence_y[-1] (right)
    # For simplicity, use angles: left = -45 deg, right = 45 deg
    # A point is fair if between these angles and y > 0
    angle = np.degrees(np.arctan2(x, y))
    return (angle < -45 or angle > 45 or y < 0)

results = []
with open('data/harper_2025_batted_balls_with_type.csv') as f:
    reader = csv.reader(f, delimiter='|')
    for row in reader:
        if len(row) >= 3:
            try:
                hc_x = float(row[0])
                hc_y = float(row[1])
                event_type = row[2].strip()
                location_x = 2.5 * (hc_x - 125.42)
                location_y = 2.5 * (198.27 - hc_y)
                if is_foul(location_x, location_y) and 'out' not in event_type:
                    results.append((location_x, location_y, event_type))
            except ValueError:
                continue

print('Non-out batted balls in foul territory:')
for x, y, event in results:
    print(f'Event: {event:12s}  x: {x:7.2f}  y: {y:7.2f}  angle: {np.degrees(np.arctan2(x, y)):.1f}')
print(f'Total: {len(results)}')
