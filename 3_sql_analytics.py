from pathlib import Path

import pandas as pd

CLEAN_DIR = Path("data/cleaned")
OUTPUT_DIR = Path("outputs/sql_results")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    cleaned_files = list(CLEAN_DIR.glob("*.parquet"))
    if not cleaned_files:
        print("No cleaned data available in data/cleaned/. Run 1_data_ingestion_cleaning.py first.")
        return

    print(f"Loading {len(cleaned_files)} cleaned files...")
    df = pd.concat([pd.read_parquet(path) for path in cleaned_files], ignore_index=True)
    df.columns = df.columns.str.lower()
    df = df.loc[:, ~df.columns.duplicated()]

    print("Computing SQL-style aggregates using pandas...")
    peak_demand = (
        df.groupby("hour", dropna=False)
        .agg(trip_count=("hour", "size"), total_revenue=("fare_amount", "sum"))
        .reset_index()
        .sort_values("trip_count", ascending=False)
        .head(10)
    )

    revenue_by_day = (
        df.groupby("day_of_week", dropna=False)
        .agg(trip_count=("day_of_week", "size"), revenue=("fare_amount", "sum"))
        .reset_index()
        .sort_values("revenue", ascending=False)
    )

    peak_demand.to_csv(OUTPUT_DIR / "peak_demand_hours.csv", index=False)
    print(f"Saved SQL query result: {OUTPUT_DIR / 'peak_demand_hours.csv'}")

    revenue_by_day.to_csv(OUTPUT_DIR / "revenue_by_day.csv", index=False)
    print(f"Saved SQL query result: {OUTPUT_DIR / 'revenue_by_day.csv'}")


if __name__ == "__main__":
    main()
