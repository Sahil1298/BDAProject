# Air Quality Analysis

This project analyzes India's air-quality observations (2015–2020) using two approaches:

- **Hadoop MapReduce** counts AQI categories by date and calculates average PM2.5 by station.
- **PySpark** performs the same analyses with DataFrame operations.
- **Streamlit** displays the generated results and lets you select the MapReduce or PySpark output.

The cleaned dataset contains `StationId`, `Datetime`, `PM2.5`, and `AQI_Bucket`.

## Project structure

```text
.
├── air_quality_cleaned.csv
├── app.py
├── mapreduce/
│   ├── mapper_aqi_bucket.py
│   ├── mapper_avg_pm25.py
│   ├── reducer_aqi_bucket.py
│   └── reducer_avg_pm25.py
├── output/
│   ├── output_aqi_bucket.csv
│   ├── output_avg_pm25.csv
│   ├── pyspark_aqi_bucket.csv
│   └── pyspark_avg_pm25.csv
├── preprocessing/
│   ├── dataPreprocessing.ipynb
│   └── textToCsvConverter.ipynb
├── pyspark/
│   ├── aqi_analysis.py
│   └── pm25_analysis.py
├── requirements.txt
├── sample_input.csv
└── stations.csv
```

## Install dependencies

Python and Java are required for PySpark. From the project root, create and activate a virtual environment, then install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run the PySpark analyses

From the project root, each script reads `air_quality_cleaned.csv`, prints a small sample, and writes its CSV result under `output/`:

```powershell
python pyspark\aqi_analysis.py
python pyspark\pm25_analysis.py
```

## Run MapReduce locally without Hadoop

The following PowerShell pipelines run the mapper, sort records by key to simulate Hadoop's shuffle, and pass them to the reducer. They display tab-separated reducer output:

```powershell
Get-Content .\air_quality_cleaned.csv | & .\.venv\Scripts\python.exe .\mapreduce\mapper_aqi_bucket.py | Sort-Object { $_.Split("`t")[0] } | & .\.venv\Scripts\python.exe .\mapreduce\reducer_aqi_bucket.py
Get-Content .\air_quality_cleaned.csv | & .\.venv\Scripts\python.exe .\mapreduce\mapper_avg_pm25.py | Sort-Object { $_.Split("`t")[0] } | & .\.venv\Scripts\python.exe .\mapreduce\reducer_avg_pm25.py
```

For a small test, replace `air_quality_cleaned.csv` with `sample_input.csv`. Its first column is `id`, so that test calculates PM2.5 by ID rather than by station.

The generated MapReduce CSV files in `output/` are formatted with headers for use by Streamlit.

## Run the Streamlit dashboard

From the project root:

```powershell
python -m streamlit run app.py
```

The dashboard reads the four generated result CSVs from `output/`; it does not launch the processing jobs itself. Use the sidebar to select a page and the results source.
