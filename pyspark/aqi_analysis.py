from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date


data_path = Path(__file__).resolve().parent.parent / "air_quality_cleaned.csv"

spark = SparkSession.builder.appName("AQI Bucket Analysis").getOrCreate()

try:
    air_quality = spark.read.csv(str(data_path), header=True, inferSchema=True)

    aqi_counts = (
        air_quality
        .withColumn("date", to_date(col("Datetime")))
        .filter(col("date").isNotNull())
        .filter(col("AQI_Bucket").isNotNull() & (col("AQI_Bucket") != "NA"))
        .groupBy("date", "AQI_Bucket")
        .count()
        .orderBy("date", "AQI_Bucket")
    )

    aqi_counts.show(10, truncate=False)
finally:
    spark.stop()
