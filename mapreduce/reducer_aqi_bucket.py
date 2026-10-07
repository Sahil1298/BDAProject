#!/usr/bin/env python3
import sys
from collections import defaultdict

current_date = None
bucket_counts = defaultdict(int)

for line in sys.stdin:
    fields = line.rstrip('\n').split('\t')
    if len(fields) != 2:
        continue

    date, bucket = (field.strip() for field in fields)
    if not date or not bucket:
        continue

    if date != current_date:
        if current_date is not None:
            for category, count in bucket_counts.items():
                print(f"{current_date}\t{category}\t{count}")
        current_date = date
        bucket_counts = defaultdict(int)

    bucket_counts[bucket] += 1

if current_date is not None:
    for category, count in bucket_counts.items():
        print(f"{current_date}\t{category}\t{count}")