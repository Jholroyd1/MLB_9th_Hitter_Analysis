import csv

# List of event types that are outs (should be excluded)
out_types = [
    'field_out', 'force_out', 'grounded_into_double_play', 'double_play', 'triple_play',
    'strikeout', 'strikeout_double_play', 'sac_fly', 'sac_bunt', 'sac_fly_double_play',
    'sac_bunt_double_play', 'pickoff', 'pickoff_caught_stealing', 'caught_stealing',
    'other_out', 'fielders_choice', 'fielders_choice_out', 'batter_interference',
    'runner_interference', 'fan_interference', 'pickoff_error', 'pickoff_1b', 'pickoff_2b', 'pickoff_3b',
    'caught_stealing_2b', 'caught_stealing_3b', 'caught_stealing_home', 'intent_walk', 'walk', 'hit_by_pitch'
]

with open('data/foul_nonout_play_by_play.csv') as infile, open('data/foul_true_nonout_play_by_play.csv', 'w', newline='') as outfile:
    reader = csv.DictReader(infile)
    writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
    writer.writeheader()
    for row in reader:
        if row['event_type'] not in out_types:
            writer.writerow(row)

print('Filtered file written to data/foul_true_nonout_play_by_play.csv')
