from pathlib import Path

import pandas as pd

CLEAN_DIR = Path("data/cleaned")
OUTPUT_DIR = Path("outputs/reports")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def compute_kpis(df: pd.DataFrame) -> dict:
    return {
        "total_trips": int(len(df)),
        "total_revenue": float(df["fare_amount"].sum()),
        "avg_distance": float(df["trip_distance"].mean()),
        "avg_fare": float(df["fare_amount"].mean()),
        "avg_tip_pct": float((df["tip_amount"] / df["fare_amount"]).replace([float("inf"), float("nan")], 0).mean()),
    }


def main():
    cleaned_files = list(CLEAN_DIR.glob("*.parquet"))
    if not cleaned_files:
        print("No cleaned data available in data/cleaned/. Run 1_data_ingestion_cleaning.py first.")
        return

    df = pd.concat([pd.read_parquet(path) for path in cleaned_files], ignore_index=True)
    kpis = compute_kpis(df)

    report_path = OUTPUT_DIR / "kpi_report.txt"
    with open(report_path, "w", encoding="utf-8") as report:
        report.write("CITY MOBILITY KPI REPORT\n")
        report.write("=======================\n")
        for key, value in kpis.items():
            report.write(f"{key}: {value}\n")

    print(f"KPI report generated: {report_path}")


if __name__ == "__main__":
    main()
