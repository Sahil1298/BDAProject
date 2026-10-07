# Air Quality Analysis Project Explanation

## 1. Problem statement and objective

Air-quality observations are recorded over time at many monitoring stations. The project uses the cleaned observations to answer two questions:

1. How many observations fall into each AQI category on each date?
2. What is the average PM2.5 value for each monitoring station?

Both questions are implemented with Python Hadoop Streaming-style MapReduce scripts and with PySpark DataFrame operations. A Streamlit app presents the generated results for either approach.

## 2. Dataset and columns

The input is `air_quality_cleaned.csv` in the project root. It has a header and about 1.88 million data rows. The columns used by the project are:

| Column | Meaning in this project |
|---|---|
| `StationId` | Identifier of the monitoring station |
| `Datetime` | Observation date and time |
| `PM2.5` | PM2.5 reading |
| `AQI_Bucket` | AQI category assigned to the observation |

The MapReduce and PySpark analyses read this cleaned file directly. `sample_input.csv` is a small fixture for local testing; its first column is `id`, not `StationId`, so its PM2.5 test groups by ID.

## 3. Project architecture and data flow

```text
air_quality_cleaned.csv
       ├── MapReduce mapper -> key sort/shuffle -> reducer
       │       └── output/output_aqi_bucket.csv
       │           output/output_avg_pm25.csv
       └── PySpark DataFrame analysis
               └── output/pyspark_aqi_bucket.csv
                   output/pyspark_avg_pm25.csv

All four result CSVs -> app.py (Streamlit) -> charts, summary metrics, tables
```

The MapReduce scripts read records from standard input and write tab-separated records to standard output. The PySpark scripts read the dataset by a path derived from their own location and write headered CSV result files into `output/`. Streamlit reads the four already-generated CSVs; it does not run either analysis.

## 4. MapReduce implementation

Each mapper reads CSV input from standard input with Python's `csv` module. It detects the header from the field names, so it does not blindly discard the first record. Short rows and empty or `NA` values are skipped.

The mapper emits a tab-separated key and value. Hadoop Streaming uses the first tab to separate the key from the value. Hadoop's shuffle/sort groups and sorts records by key before they reach a reducer. The reducers here rely on all records for a key being consecutive.

For a local demonstration without Hadoop, the shell commands below run the mapper, sort emitted lines by their first tab-separated field, and run the reducer. That sort step simulates the key ordering that Hadoop normally supplies.

### AQI category counts by date

- `mapreduce/mapper_aqi_bucket.py` reads `Datetime` and `AQI_Bucket`, extracts the date part, and emits `date<TAB>AQI_Bucket`.
- `mapreduce/reducer_aqi_bucket.py` groups consecutive date keys, counts each bucket for that date, and emits `date<TAB>AQI_Bucket<TAB>count`.

Example mapper input:

```csv
StationId,Datetime,PM2.5,AQI_Bucket
AP001,2017-11-25 09:00:00,104.0,Moderate
```

Mapper output:

```text
2017-11-25	Moderate
```

Reducer output:

```text
2017-11-25	Moderate	1
```

### Average PM2.5 by station

- `mapreduce/mapper_avg_pm25.py` reads `StationId` and `PM2.5`, then emits `StationId<TAB>PM2.5`.
- `mapreduce/reducer_avg_pm25.py` converts numeric values, skips malformed and non-finite readings, and computes the arithmetic mean for each consecutive station key. Its output average is rounded to two decimal places.

Example mapper input and output:

```csv
StationId,Datetime,PM2.5,AQI_Bucket
AP001,2017-11-25 09:00:00,104.0,Moderate
```

```text
AP001	104.0
```

If the sorted reducer input contains `AP001<TAB>104.0` and `AP001<TAB>94.5`, the reducer emits:

```text
AP001	99.25
```

## 5. PySpark implementation

The scripts in `pyspark/` use PySpark DataFrames:

- `pyspark/aqi_analysis.py` parses `Datetime` into a date, excludes invalid dates and missing/`NA` buckets, groups by date and `AQI_Bucket`, and counts observations.
- `pyspark/pm25_analysis.py` excludes missing, blank, `NA`, and non-numeric PM2.5 values, groups by `StationId`, and calculates `avg`.

Each script prints up to ten result rows and writes a headered CSV:

| Script | CSV output | Header |
|---|---|---|
| `pyspark/aqi_analysis.py` | `output/pyspark_aqi_bucket.csv` | `date,AQI_Bucket,count` |
| `pyspark/pm25_analysis.py` | `output/pyspark_avg_pm25.csv` | `StationId,Avg_PM25` |

Unlike the streaming-style reducers, the PySpark scripts express grouping and aggregation as DataFrame operations. The PM2.5 result keeps Spark's average precision rather than rounding to two decimal places.

## 6. Streamlit dashboard and result flow

`app.py` loads all four result CSVs from `output/`, normalizes their differing column names, and offers a sidebar choice between **MapReduce** and **PySpark** results. It does not launch the mappers, reducers, or Spark scripts.

The dashboard has three pages:

- **Dashboard:** AQI count total, station/date counts, average PM2.5, AQI-over-time area chart, highest-station bar chart, AQI category pie chart, and highest station summary.
- **AQI Trends:** year and category filters, a daily line chart, category summary bar chart, and a table of processed AQI results.
- **PM2.5 Analysis:** adjustable top-station bar chart, high/average/low summary metrics, PM2.5 histogram, and a station lookup table.

The app expects all four result files to be present and contain usable rows. If results are missing or invalid, it displays an error instead of running the jobs.

## 7. Important files and folders

| Path | Purpose |
|---|---|
| `air_quality_cleaned.csv` | Input dataset for both analysis implementations |
| `mapreduce/mapper_aqi_bucket.py` | AQI mapper |
| `mapreduce/reducer_aqi_bucket.py` | AQI date/category counter |
| `mapreduce/mapper_avg_pm25.py` | PM2.5 mapper |
| `mapreduce/reducer_avg_pm25.py` | Station average reducer |
| `pyspark/aqi_analysis.py` | PySpark AQI aggregation |
| `pyspark/pm25_analysis.py` | PySpark station averages |
| `output/` | Generated result CSVs used by the dashboard; it also contains tab-separated MapReduce output examples |
| `app.py` | Streamlit frontend |
| `requirements.txt` | Pinned Python dependencies |
| `preprocessing/` | Notebooks documenting preprocessing and an older tab-to-comma conversion |
| `sample_input.csv` | Small local pipeline test input |
| `stations.csv` | Station metadata reference file; current scripts and dashboard do not use it |

## 8. Setup and run steps

These commands are for Windows PowerShell, run from the project root. Python and a Java runtime compatible with the installed PySpark version are required for PySpark.

### Install dependencies

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

The dependencies are pinned in `requirements.txt`: PySpark, pandas, Plotly, and Streamlit.

### Run the PySpark jobs

```powershell
python .\pyspark\aqi_analysis.py
python .\pyspark\pm25_analysis.py
```

These read `air_quality_cleaned.csv`, print a sample to the console, and write the two `pyspark_*.csv` files in `output/`.

### Run the MapReduce pipelines locally

Hadoop is not needed for this local simulation. The commands pipe the complete CSV through a mapper, sort mapper records by key, and pass the sorted records to a reducer:

```powershell
Get-Content -Encoding UTF8 .\air_quality_cleaned.csv | & .\.venv\Scripts\python.exe .\mapreduce\mapper_aqi_bucket.py | Sort-Object { $_.Split("`t")[0] } | & .\.venv\Scripts\python.exe .\mapreduce\reducer_aqi_bucket.py

Get-Content -Encoding UTF8 .\air_quality_cleaned.csv | & .\.venv\Scripts\python.exe .\mapreduce\mapper_avg_pm25.py | Sort-Object { $_.Split("`t")[0] } | & .\.venv\Scripts\python.exe .\mapreduce\reducer_avg_pm25.py
```

The reducer output is tab-separated and displayed in the terminal. These commands do not write or refresh the CSV files consumed by Streamlit; the committed MapReduce CSVs in `output/` are pre-generated results. For a quick test, substitute `sample_input.csv` for the cleaned dataset.

### Run Streamlit

```powershell
python -m streamlit run .\app.py
```

Open the local URL printed by Streamlit. Select the page and the result source in the sidebar.

## 9. Example result files

The files in `output/` are CSVs with headers, suitable for spreadsheet tools and the dashboard.

AQI MapReduce result (`output/output_aqi_bucket.csv`):

```csv
Date,AQI_Category,Count
2015-01-01,Severe,8
2015-01-01,Very Poor,8
```

PM2.5 MapReduce result (`output/output_avg_pm25.csv`):

```csv
Station_ID,Avg_PM25
AP001,38.75
AP005,48.27
```

PySpark equivalents use headers `date,AQI_Bucket,count` and `StationId,Avg_PM25`; AQI values represent the same count analysis, while PM2.5 averages retain more decimal places.

## 10. Why use MapReduce and PySpark?

MapReduce demonstrates the map, shuffle/sort, and reduce pattern for distributed batch processing. PySpark demonstrates the same grouping and aggregation using a higher-level DataFrame API, which is usually more concise for these operations. Comparing the two helps explain distributed processing concepts and their programming styles. In this project, the dashboard visualizes saved results; it is not a live benchmark of the frameworks.

## 11. Limitations and current scope

- The implemented analyses are limited to AQI category counts by date and average PM2.5 by station. The project does not implement the broader city ranking or PM2.5-over-time analyses suggested by some project descriptions.
- The local MapReduce commands simulate shuffle/sort with PowerShell sorting; they are not a Hadoop cluster or HDFS execution.
- The reducers require input sorted by key. Feeding unsorted mapper records directly to them can split a key's group and produce partial results.
- The local sort pipeline buffers/sorts emitted records and is for demonstration, not a scalable replacement for Hadoop.
- PySpark and MapReduce outputs may differ slightly in PM2.5 precision because the MapReduce reducer rounds to two decimals and PySpark writes the average at higher precision.
- Result CSV files are generated separately from Streamlit. If the input dataset changes, rerun the analysis and refresh the corresponding outputs before using the dashboard.
- `preprocessing/dataPreprocessing.ipynb` refers to `station_hour.csv`, which is not included. The preprocessing notebook therefore documents the workflow but cannot be rerun from the current repository alone.
- `stations.csv` is included as reference data but is not joined into the analyses or dashboard.

## 12. Beginner-friendly project walkthrough

Think of each CSV row as one station measurement at one time. For AQI, the mapper keeps the date and category. For PM2.5, it keeps the station and reading. A distributed framework sends records with the same key to the same reducer, after ordering them by key. The AQI reducer counts category occurrences; the PM2.5 reducer adds readings and divides by their count.

The PySpark versions describe these transformations with DataFrame operations: filter invalid values, group rows, then count or average. Each approach writes a result CSV. Finally, Streamlit loads those result files, changes column labels to a common format, and draws charts and tables. This separation means processing can be run independently, while the dashboard remains focused on showing the saved analysis.

## 13. Viva questions and concise answers

1. **What is the goal of this project?**  
   Count AQI categories per date and calculate average PM2.5 per station.

2. **What does the AQI mapper emit?**  
   A date key and an AQI bucket value, separated by a tab.

3. **What is shuffle and sort?**  
   Hadoop groups mapper records by key and orders keys before sending records to reducers.

4. **Why must the reducer input be sorted?**  
   These reducers detect when the key changes to know when to finish an aggregation.

5. **How does the AQI reducer work?**  
   It counts each category while processing the records for one date.

6. **How does the PM2.5 reducer work?**  
   It sums numeric readings and divides by the number of readings for each station.

7. **What is the difference between MapReduce and PySpark here?**  
   MapReduce uses explicit mapper/reducer scripts and tab-separated records; PySpark uses DataFrame transformations and aggregations.

8. **Why does the mapper skip a header by checking its labels?**  
   Hadoop may give each mapper a split beginning with a data row; blindly skipping the first row could lose data.

9. **How are invalid PM2.5 values handled?**  
   MapReduce skips nonnumeric/non-finite values in its reducer; PySpark filters missing/blank/`NA` values and drops values that cannot be cast to numbers.

10. **Does Streamlit run Spark or Hadoop?**  
    No. It loads pre-generated CSV result files from `output/`.

11. **Why can PM2.5 results have different decimal digits?**  
    The MapReduce reducer formats averages to two decimal places; PySpark preserves more precision in its output CSV.

12. **Is the local PowerShell pipeline a Hadoop cluster run?**  
    No. It runs the Python scripts locally and simulates the shuffle/sort step.

