import importlib.util
from pathlib import Path


if __name__ == "__main__":
    ROOT_DIR = Path(__file__).resolve().parent
    DASHBOARD_PATH = ROOT_DIR / "frontend" / "dashboard.py"

    spec = importlib.util.spec_from_file_location("dashboard_app", DASHBOARD_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load dashboard from {DASHBOARD_PATH}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.main()
