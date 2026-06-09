from pathlib import Path

import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.functions import hour

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def fallback_etl():
    raw_files = sorted(RAW_DIR.glob("*.csv"))
    if not raw_files:
        print("No raw CSV files found in data/raw/. Add dataset files and rerun.")
        return

    print("Spark ETL failed. Falling back to pandas-based CSV to Parquet processing.")
    part_index = 0
    for path in raw_files:
        for chunk in pd.read_csv(path, chunksize=200000):
            chunk.columns = chunk.columns.str.lower()
            datetime_cols = ["pickup_datetime", "tpep_pickup_datetime", "lpep_pickup_datetime"]
            pickup_col = next((col for col in datetime_cols if col in chunk.columns), None)
            if pickup_col is None:
                continue

            chunk = chunk[chunk["trip_distance"] > 0]
            chunk["pickup_datetime"] = pd.to_datetime(chunk[pickup_col], errors="coerce")
            chunk = chunk.dropna(subset=["pickup_datetime"])
            chunk["hour"] = chunk["pickup_datetime"].dt.hour
            chunk.to_parquet(PROCESSED_DIR / f"taxi_data_part_{part_index}.parquet", index=False)
            print(f"Wrote part file taxi_data_part_{part_index}.parquet")
            part_index += 1

    if part_index == 0:
        print("Fallback ETL did not write any parquet files.")
    else:
        print(f"Fallback ETL wrote {part_index} parquet file(s) to {PROCESSED_DIR}")


def main():
    try:
        spark = (
            SparkSession.builder
            .appName("MobilityETL")
            .master("local[*]")
            .config("spark.driver.host", "127.0.0.1")
            .config("spark.hadoop.dfs.permissions.enabled", "false")
            .config("spark.hadoop.fs.permissions.umask-mode", "000")
            .getOrCreate()
        )
        raw_files = [str(path) for path in RAW_DIR.glob("*.csv")]
        if not raw_files:
            print("No raw CSV files found in data/raw/. Add dataset files and rerun.")
            spark.stop()
            return

        df = spark.read.option("header", "true").option("inferSchema", "true").csv(raw_files)
        cols = [c.lower() for c in df.columns]
        df = df.toDF(*cols)

        datetime_cols = ["pickup_datetime", "tpep_pickup_datetime", "lpep_pickup_datetime"]
        pickup_col = next((col for col in datetime_cols if col in df.columns), None)
        if pickup_col is None:
            print("No pickup datetime column found in dataset.")
            spark.stop()
            return

        if "trip_distance" not in df.columns:
            print("No trip_distance column found in dataset.")
            spark.stop()
            return

        df = df.filter(df.trip_distance > 0)
        df = df.withColumn("pickup_datetime", df[pickup_col].cast("timestamp"))
        df = df.withColumn("hour", hour(df["pickup_datetime"]))
        df.write.mode("overwrite").parquet(str(PROCESSED_DIR / "taxi_data.parquet"))

        print(f"Processed data saved to {PROCESSED_DIR / 'taxi_data.parquet'}")
        spark.stop()
    except Exception as exc:
        error_message = str(exc)
        if "HADOOP_HOME and hadoop.home.dir are unset" in error_message or "winutils.exe" in error_message:
            print("Spark on Windows requires Hadoop winutils.exe to write local files.")
            print("Set HADOOP_HOME or hadoop.home.dir to a folder containing bin\\winutils.exe, then rerun the script.")
            print("Example: set HADOOP_HOME=C:\\hadoop && set PATH=%HADOOP_HOME%\\bin;%PATH%")
        print(f"Spark ETL failed: {exc}")
        fallback_etl()


if __name__ == "__main__":
    main()
