from pathlib import Path

SCRIPTS = [
    "1_data_ingestion_cleaning.py",
    "2_kpi_computation.py",
    "3_sql_analytics.py",
    "4_pyspark_etl.py",
    "5_genai_assistant.py",
]

if __name__ == "__main__":
    base = Path(__file__).parent
    for script in SCRIPTS:
        path = base / script
        if path.exists():
            print(f"Running {script}...")
            exec(path.read_text(), {"__name__": "__main__"})
        else:
            print(f"Missing script: {script}")
