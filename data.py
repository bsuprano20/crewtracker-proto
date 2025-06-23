import pandas as pd

# Sample master tables
JOBS = pd.DataFrame([
    {"id": 1, "name": "Kenyon"},
    {"id": 2, "name": "TWHS"},
])

COST_CODES = pd.DataFrame([
    {"id": 101, "code": "CC101", "description": "Masonry", "pmph_goal": 10},
    {"id": 202, "code": "CC202", "description": "Framing", "pmph_goal": 8},
])

# Load or initialize entries.csv
try:
    ENTRIES = pd.read_csv("entries.csv", parse_dates=["date"])
except FileNotFoundError:
    ENTRIES = pd.DataFrame(columns=[
        "date", "job_id", "cost_code_id", "hours", "units_installed"
    ])
