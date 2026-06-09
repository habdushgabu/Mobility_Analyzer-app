import importlib.util
from pathlib import Path


if __name__ == "__main__":
    ROOT_DIR = Path(__file__).resolve().parent
    DASHBOARD_PATH = ROOT_DIR / "frontend" / "dashboard.py"

    if not DASHBOARD_PATH.exists():
        raise FileNotFoundError(
            f"Streamlit dashboard file is missing: {DASHBOARD_PATH}. "
            "Make sure frontend/dashboard.py is committed and pushed to GitHub."
        )

    spec = importlib.util.spec_from_file_location("dashboard_app", DASHBOARD_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load dashboard from {DASHBOARD_PATH}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.main()
