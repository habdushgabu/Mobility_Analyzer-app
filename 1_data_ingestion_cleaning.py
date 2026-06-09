import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

load_dotenv()

RAW_DIR = Path("data/raw")
CLEAN_DIR = Path("data/cleaned")
CLEAN_DIR.mkdir(parents=True, exist_ok=True)

class MobilityDataAnalyzer:
    def __init__(self, raw_dir: Path, clean_dir: Path):
        self.raw_dir = raw_dir
        self.clean_dir = clean_dir

    def load_data(self, filename: str) -> pd.DataFrame:
        path = self.raw_dir / filename
        return pd.read_csv(path)

    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        datetime_cols = ["pickup_datetime", "tpep_pickup_datetime", "lpep_pickup_datetime"]
        pickup_col = next((col for col in datetime_cols if col in df.columns), None)
        if pickup_col is None:
            raise ValueError("No pickup datetime column found in dataset.")

        distance_cols = ["trip_distance", "trip_dist", "distance"]
        distance_col = next((col for col in distance_cols if col in df.columns), None)
        if distance_col is None:
            raise ValueError("No trip distance column found in dataset.")

        df = df.dropna(how="any")
        df = df[df[distance_col] > 0]
        df["pickup_datetime"] = pd.to_datetime(df[pickup_col], errors="coerce")
        df = df.dropna(subset=["pickup_datetime"])
        df["hour"] = df["pickup_datetime"].dt.hour
        df["day_of_week"] = df["pickup_datetime"].dt.day_name()
        df["month"] = df["pickup_datetime"].dt.month

        if distance_col != "trip_distance":
            df["trip_distance"] = df[distance_col]

        return df

    def save(self, df: pd.DataFrame, filename: str):
        df.to_parquet(self.clean_dir / filename, index=False)


def main():
    analyzer = MobilityDataAnalyzer(RAW_DIR, CLEAN_DIR)
    raw_files = [f.name for f in RAW_DIR.glob("*.csv")]
    if not raw_files:
        print("No raw CSV files found in data/raw/. Add dataset files and rerun.")
        return

    for name in raw_files:
        print(f"Processing {name}")
        df = analyzer.load_data(name)
        df_clean = analyzer.clean(df)
        output_name = name.replace(".csv", ".parquet")
        analyzer.save(df_clean, output_name)
        print(f"Saved cleaned file to {CLEAN_DIR / output_name}")


if __name__ == "__main__":
    main()
