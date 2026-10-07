# Air Quality Analysis using Hadoop MapReduce

**Detecting the Most Polluted Locations and Times (India, 2015–2020)**

This project aims to analyze large-scale air quality data from India using Hadoop MapReduce. By processing over 1.8 million records, we uncover patterns in pollution levels across cities and time periods.

---

## Project Objective

To design and implement a scalable MapReduce pipeline to:

* Analyze air quality distribution by date
* Identify the most polluted cities and monitoring stations
* Understand PM2.5 concentration trends over time

---

## Dataset Overview

The dataset used is titled **"Air Quality Data in India (2015–2020)"** and was sourced from Kaggle:
[https://www.kaggle.com/datasets/rohanrao/air-quality-data-in-india](https://www.kaggle.com/datasets/rohanrao/air-quality-data-in-india)

Key Information:

* Original records: \~2.5 million
* After preprocessing: \~1.8 million
* Format: CSV
* Monitored fields (retained):

  * `StationId`
  * `Datetime`
  * `PM2.5`
  * `AQI_Bucket`
* Data cleaning was performed using Python (pandas), and the final file is saved as `air_quality_cleaned.csv`.

---

## Tools and Technologies

| Tool                | Purpose                         |
| ------------------- | ------------------------------- |
| Python (pandas)     | Data cleaning and preprocessing |
| Apache Hadoop       | MapReduce framework             |
| Hadoop Streaming    | Using Python as mapper/reducer  |
| HDFS                | Distributed storage             |
| VirtualBox + Ubuntu | Local environment setup         |
| Java JDK 8          | Required for Hadoop runtime     |

---

## MapReduce Tasks Implemented

### 1. AQI Bucket Distribution by Date

* **Mapper**: Emits (date, AQI bucket)
* **Reducer**: Counts occurrences of each AQI bucket per date

### 2. Average PM2.5 by Monitoring Station

* **Mapper**: Emits (station ID, PM2.5)
* **Reducer**: Calculates the average PM2.5 value per station

---

## Repository Contents

| File                      | Description                                  |
| ------------------------- | -------------------------------------------- |
| `mapper_aqi_bucket.py`    | Mapper script for AQI distribution by date   |
| `reducer_aqi_bucket.py`   | Reducer script for counting AQI buckets      |
| `mapper_avg_pm25.py`      | Mapper script for PM2.5 per station          |
| `reducer_avg_pm25.py`     | Reducer script for calculating PM2.5 average |
| `air_quality_cleaned.csv` | Cleaned dataset                              |
| `sample_input.csv`        | Sample test input for local runs             |

---

## How to Run This Project

### Prerequisites

* Java JDK 8 installed
* Hadoop installed and configured
* HDFS up and running
* Python installed on the same environment as Hadoop

---

### Step 1: Upload Dataset to HDFS

```bash
hdfs dfs -mkdir -p /airquality/input
hdfs dfs -put air_quality_cleaned.csv /airquality/input/
```

---

### Step 2: Run AQI Bucket Distribution MapReduce Job

```bash
hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming.jar \
  -input /airquality/input/air_quality_cleaned.csv \
  -output /airquality/output_aqi_bucket \
  -mapper mapper_aqi_bucket.py \
  -reducer reducer_aqi_bucket.py
```

---

### Step 3: Run Average PM2.5 by Station MapReduce Job

```bash
hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming.jar \
  -input /airquality/input/air_quality_cleaned.csv \
  -output /airquality/output_avg_pm25 \
  -mapper mapper_avg_pm25.py \
  -reducer reducer_avg_pm25.py
```

---

### Step 4: View the Results

```bash
hdfs dfs -cat /airquality/output_aqi_bucket/part-00000
hdfs dfs -cat /airquality/output_avg_pm25/part-00000
```

## Outcome

This project demonstrates:

* Effective preprocessing of large-scale environmental data
* Building and executing custom Python-based MapReduce jobs
* Gaining insights into pollution levels and patterns across Indian cities


