from pathlib import Path
import subprocess
import sys

SCRIPTS = [
    "1_data_ingestion_cleaning.py",
    "2_kpi_computation.py",
    "3_sql_analytics.py",
]


if __name__ == "__main__":
    base = Path(__file__).parent
    for script in SCRIPTS:
        path = base / script
        if not path.exists():
            print(f"Missing script: {script}")
            continue

        print(f"\n=== Running {script} ===")
        subprocess.run([sys.executable, str(path)], check=True)

    print("\nNon-Spark pipeline finished.")
    print("Spark ETL is optional for this project; the fallback path is already in place.")
