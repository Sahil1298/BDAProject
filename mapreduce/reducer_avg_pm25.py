import sys
import math

current_station = None
total = 0.0
count = 0

for line in sys.stdin:
    fields = line.rstrip('\n').split('\t')
    if len(fields) != 2:
        continue

    station, raw_value = (field.strip() for field in fields)
    if not station or not raw_value:
        continue

    try:
        val = float(raw_value)
    except ValueError:
        continue

    if not math.isfinite(val):
        continue

    if station == current_station:
        total += val
        count += 1
    else:
        if current_station is not None:
            print(f"{current_station}\t{total/count:.2f}")

        current_station = station
        total = val
        count = 1

if current_station is not None:
    print(f"{current_station}\t{total/count:.2f}")
