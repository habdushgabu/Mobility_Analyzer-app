import importlib.util
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

BASE_DIR = Path(__file__).resolve().parents[1]
GENAI_MODULE = BASE_DIR / "5_genai_assistant.py"
SPEC = importlib.util.spec_from_file_location("genai_assistant", GENAI_MODULE)
GENAI = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GENAI)
ask_groq = GENAI.ask_groq

st.set_page_config(page_title="Urban Mobility Analytics", layout="wide")

BASE_DIR = Path(__file__).resolve().parents[1]
REPORTS_DIR = BASE_DIR / "outputs" / "reports"
SQL_DIR = BASE_DIR / "outputs" / "sql_results"
PROCESSED_DIR = BASE_DIR / "data" / "processed"


def load_kpi_report(path: Path) -> dict:
    metrics = {}
    if path.exists():
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            if ":" in raw_line:
                key, value = raw_line.split(":", 1)
                try:
                    metrics[key.strip().lower()] = float(value.strip())
                except ValueError:
                    metrics[key.strip().lower()] = value.strip()
    return metrics


st.title("🚕 Intelligent Urban Mobility Analytics")
st.write("This local dashboard uses the generated KPI, SQL, and parquet outputs already produced in the project.")

kpi = load_kpi_report(REPORTS_DIR / "kpi_report.txt")
peak_df = pd.read_csv(SQL_DIR / "peak_demand_hours.csv") if (SQL_DIR / "peak_demand_hours.csv").exists() else pd.DataFrame()
revenue_df = pd.read_csv(SQL_DIR / "revenue_by_day.csv") if (SQL_DIR / "revenue_by_day.csv").exists() else pd.DataFrame()
part_files = sorted(PROCESSED_DIR.glob("taxi_data_part_*.parquet")) if PROCESSED_DIR.exists() else []


tabs = st.tabs(["Dashboard Overview", "Visual Analytics", "SQL Insights", "Processed Outputs", "GenAI Chatbot"])

with tabs[0]:
    st.header("Dashboard Overview")
    st.caption("Current KPI snapshot from the non-Spark pipeline run.")
    cols = st.columns(4)
    if "total_trips" in kpi:
        cols[0].metric("Total trips", f"{int(kpi['total_trips']):,}")
    if "total_revenue" in kpi:
        cols[1].metric("Total revenue", f"${kpi['total_revenue']:,.2f}")
    if "avg_distance" in kpi:
        cols[2].metric("Avg. distance", f"{kpi['avg_distance']:.2f} mi")
    if "avg_fare" in kpi:
        cols[3].metric("Avg. fare", f"${kpi['avg_fare']:.2f}")

with tabs[1]:
    st.header("Visual Analytics")
    if not peak_df.empty:
        fig1 = px.bar(peak_df.head(10), x="hour", y="trip_count", title="Peak demand by hour")
        st.plotly_chart(fig1, use_container_width=True)
    if not revenue_df.empty:
        fig2 = px.bar(revenue_df, x="day_of_week", y="revenue", title="Revenue by weekday")
        st.plotly_chart(fig2, use_container_width=True)
    if peak_df.empty and revenue_df.empty:
        st.info("No chart data is available yet. Run the pipeline to generate SQL outputs.")

with tabs[2]:
    st.header("SQL Insights")
    st.write("Saved SQL-style outputs already generated in the project.")
    if not peak_df.empty:
        st.subheader("Peak demand hours")
        st.dataframe(peak_df.head(10), use_container_width=True)
    if not revenue_df.empty:
        st.subheader("Revenue by day")
        st.dataframe(revenue_df, use_container_width=True)
    if peak_df.empty and revenue_df.empty:
        st.info("No SQL result files were found in outputs/sql_results/.")

with tabs[3]:
    st.header("Processed Outputs")
    st.write(f"Fallback Parquet part files found: {len(part_files)}")
    if part_files:
        st.code("\n".join(path.name for path in part_files[:20]), language="text")
    else:
        st.info("No fallback parquet parts were found in data/processed/.")

with tabs[4]:
    st.header("GenAI Chatbot")
    st.write("Ask for a summary of the dashboard data. The assistant uses your GROQ key when available.")
    question = st.text_input("Ask a question about the mobility data", placeholder="Example: What are the busiest hours?")
    if st.button("Submit") and question:
        with st.spinner("Generating response..."):
            answer = ask_groq(question)
        st.success(answer)
