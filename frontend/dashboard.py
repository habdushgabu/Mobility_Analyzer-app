import importlib.util
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


def find_repo_root(start: Path) -> Path:
    candidates = [start, start.parent, start.parent.parent]
    for candidate in candidates:
        if (candidate / "5_genai_assistant.py").exists() and (candidate / "outputs").exists():
            return candidate
    return start.parent.parent


def load_ask_groq() -> callable:
    repo_root = find_repo_root(Path(__file__).resolve())
    genai_path = repo_root / "5_genai_assistant.py"

    if not genai_path.exists():
        raise FileNotFoundError(f"Could not find 5_genai_assistant.py under {repo_root}")

    spec = importlib.util.spec_from_file_location("genai_assistant", genai_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load genai module from {genai_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.ask_groq


ask_groq = load_ask_groq()


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


def main() -> None:
    st.set_page_config(page_title="Urban Mobility Analytics", layout="wide")

    repo_root = find_repo_root(Path(__file__).resolve())
    reports_dir = repo_root / "outputs" / "reports"
    sql_dir = repo_root / "outputs" / "sql_results"
    processed_dir = repo_root / "data" / "processed"

    st.title("🚕 Intelligent Urban Mobility Analytics")
    st.write("This local dashboard uses the generated KPI, SQL, and parquet outputs already produced in the project.")

    kpi = load_kpi_report(reports_dir / "kpi_report.txt")
    peak_df = pd.read_csv(sql_dir / "peak_demand_hours.csv") if (sql_dir / "peak_demand_hours.csv").exists() else pd.DataFrame()
    revenue_df = pd.read_csv(sql_dir / "revenue_by_day.csv") if (sql_dir / "revenue_by_day.csv").exists() else pd.DataFrame()
    part_files = sorted(processed_dir.glob("taxi_data_part_*.parquet")) if processed_dir.exists() else []

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


if __name__ == "__main__":
    main()
