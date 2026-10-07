#!/usr/bin/env python3
import sys
import csv

reader = csv.reader(sys.stdin)

for row in reader:
    if len(row) < 3:
        continue

    if row[0].strip().lstrip('\ufeff').lower() == 'stationid' and row[2].strip().lower() == 'pm2.5':
        continue

    station = row[0].strip()
    pm25 = row[2].strip()
    if station and pm25 and pm25.upper() != 'NA':
        print(f"{station}\t{pm25}")