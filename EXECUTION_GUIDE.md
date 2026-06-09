# Execution Guide

## Install dependencies
```bash
pip install -r requirements.txt
```

## Set up environment
1. Copy `.env.example` to `.env`
2. Add `GROQ_API_KEY`
3. Add Kaggle credentials if you want dataset download automation

## Run the pipeline
```bash
python run_all.py
```

## Run the frontend
```bash
streamlit run frontend/dashboard.py
```

## File locations
- Raw CSVs: `data/raw/`
- Cleaned CSVs: `data/cleaned/`
- Processed outputs: `data/processed/`
- Dashboard: `frontend/dashboard.py`
