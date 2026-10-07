from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, col, trim, upper


data_path = Path(__file__).resolve().parent.parent / "air_quality_cleaned.csv"

spark = SparkSession.builder.appName("Average PM2.5 by Station").getOrCreate()

try:
    air_quality = spark.read.csv(str(data_path), header=True, inferSchema=True)
    pm25 = col("`PM2.5`")

    pm25_averages = (
        air_quality
        .filter(pm25.isNotNull())
        .filter(trim(pm25) != "")
        .filter(upper(trim(pm25)) != "NA")
        .withColumn("pm25_value", pm25.cast("double"))
        .filter(col("pm25_value").isNotNull())
        .groupBy("StationId")
        .agg(avg("pm25_value").alias("Avg_PM25"))
        .orderBy("StationId")
    )

    pm25_averages.show(10, truncate=False)
finally:
    spark.stop()
