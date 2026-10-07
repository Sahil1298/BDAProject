#!/usr/bin/env python3
import sys
import csv

reader = csv.reader(sys.stdin)

for row in reader:
    if len(row) < 4:
        continue

    if row[1].strip().lower() == 'datetime' and row[3].strip().lower() == 'aqi_bucket':
        continue

    timestamp = row[1].strip()
    aqi_bucket = row[3].strip()
    if timestamp and aqi_bucket and aqi_bucket.upper() != 'NA':
        date = timestamp.split()[0]
        print(f"{date}\t{aqi_bucket}")