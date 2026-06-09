# Intelligent Urban Mobility Analytics & GenAI Platform

An end-to-end analytics system for urban transportation data with data cleaning, KPI computation, SQL analytics, optional PySpark ETL, GenAI insights, and a Streamlit frontend.

## Quick Start

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Create a `.env` file from `.env.example` and add your API keys for local use.

3. Run the non-Spark pipeline:

```bash
python run_without_spark.py
```

4. Launch the Streamlit frontend:

```bash
streamlit run app.py
```

## Streamlit Cloud

Use `app.py` as the main file path. Add `GROQ_API_KEY` in Streamlit secrets if you want the GenAI chatbot to work after deployment.

## Notes

- The deployed Streamlit app does not require Parquet files.
- Generated CSV/report files in `outputs/` provide the dashboard KPIs and charts.
- Raw datasets can stay local if they are too large for GitHub.

## Project Structure

- `data/raw/` - raw input files
- `data/cleaned/` - cleaned dataset outputs
- `data/processed/` - optional processed Parquet outputs
- `outputs/sql_results/` - SQL query exports
- `outputs/reports/` - generated reports
- `frontend/` - Streamlit dashboard
- `notebooks/` - exploratory analysis notebooks
