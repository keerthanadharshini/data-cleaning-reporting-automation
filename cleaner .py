"""
cleaner.py
----------
Standalone data-cleaning pipeline.
Reads raw_data.csv, cleans it, writes cleaned_data.csv + report.csv,
and returns a stats dict that app.py can consume directly.
"""

import pandas as pd
import numpy as np
import os
import json
from datetime import datetime

# ── Paths (relative to this file) ────────────────────────────────────────────
BASE_DIR    = os.path.dirname(__file__)
RAW_PATH    = os.path.join(BASE_DIR, "raw_data.csv")
CLEAN_PATH  = os.path.join(BASE_DIR, "cleaned_data.csv")
REPORT_PATH = os.path.join(BASE_DIR, "report.csv")


# ─────────────────────────────────────────────────────────────────────────────
def load_raw() -> pd.DataFrame:
    """Load raw CSV and return a DataFrame."""
    df = pd.read_csv(RAW_PATH, dtype=str)   # read everything as str first
    return df


# ─────────────────────────────────────────────────────────────────────────────
def audit(df: pd.DataFrame) -> dict:
    """
    Snapshot the dataset *before* cleaning so we can report on what changed.
    Returns a plain dict consumed by the report and the dashboard.
    """
    missing_per_col = df.replace("", np.nan).isnull().sum().to_dict()
    total_missing   = int(sum(missing_per_col.values()))
    duplicates      = int(df.duplicated().sum())

    return {
        "total_raw":        len(df),
        "total_missing":    total_missing,
        "missing_per_col":  missing_per_col,
        "duplicates":       duplicates,
    }


# ─────────────────────────────────────────────────────────────────────────────
def clean(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Full cleaning pipeline.  Returns (cleaned_df, stats_dict).

    Steps
    -----
    1.  Standardise text columns (strip whitespace, title-case)
    2.  Remove duplicate rows
    3.  Coerce numeric columns; mark invalid entries as NaN
    4.  Drop rows where Age or Sales are still invalid after coercion
    5.  Fill remaining NaNs (numeric → median, text → 'Unknown')
    6.  Reset index
    """
    before = audit(df)

    # ── Step 1 · Standardise text ──────────────────────────────────────────
    text_cols = ["Name", "City"]
    for col in text_cols:
        df[col] = (
            df[col]
            .astype(str)
            .str.strip()                 # remove leading/trailing whitespace
            .str.title()                 # Title Case  →  "mumbai" → "Mumbai"
            .replace({"Nan": np.nan, "": np.nan})
        )

    # ── Step 2 · Remove duplicates ─────────────────────────────────────────
    df = df.drop_duplicates()

    # ── Step 3 · Coerce numeric columns ───────────────────────────────────
    df["Age"]   = pd.to_numeric(df["Age"],   errors="coerce")
    df["Sales"] = pd.to_numeric(df["Sales"], errors="coerce")

    # ── Step 4 · Drop rows with out-of-range or coercion-failed values ─────
    #  Age:   must be 1–120
    #  Sales: must be > 0
    invalid_age   = df["Age"].isna()   | (df["Age"]   < 1)  | (df["Age"]   > 120)
    invalid_sales = df["Sales"].isna() | (df["Sales"] <= 0)

    rows_dropped = int((invalid_age | invalid_sales).sum())
    df = df[~(invalid_age | invalid_sales)].copy()

    # ── Step 5 · Fill remaining NaNs ──────────────────────────────────────
    df["Age"]   = df["Age"].fillna(df["Age"].median())
    df["Sales"] = df["Sales"].fillna(df["Sales"].median())
    df["Name"]  = df["Name"].fillna("Unknown")
    df["City"]  = df["City"].fillna("Unknown")

    # ── Step 6 · Tidy dtypes & index ──────────────────────────────────────
    df["Age"]   = df["Age"].astype(int)
    df["Sales"] = df["Sales"].round(2)
    df          = df.reset_index(drop=True)

    after = {
        "total_clean":    len(df),
        "rows_dropped":   rows_dropped,
    }

    stats = {**before, **after}
    return df, stats


# ─────────────────────────────────────────────────────────────────────────────
def build_report(stats: dict, df_clean: pd.DataFrame) -> pd.DataFrame:
    """
    Flatten stats + per-column missing counts into a tidy report DataFrame
    and save it to report.csv.
    """
    rows = [
        {"Metric": "Raw Records",          "Value": stats["total_raw"]},
        {"Metric": "Duplicates Removed",   "Value": stats["duplicates"]},
        {"Metric": "Total Missing Values", "Value": stats["total_missing"]},
        {"Metric": "Invalid Rows Dropped", "Value": stats["rows_dropped"]},
        {"Metric": "Final Clean Records",  "Value": stats["total_clean"]},
        {"Metric": "Avg Age (clean)",      "Value": round(df_clean["Age"].mean(), 1)},
        {"Metric": "Avg Sales (clean)",    "Value": round(df_clean["Sales"].mean(), 2)},
        {"Metric": "Total Sales (clean)",  "Value": round(df_clean["Sales"].sum(), 2)},
        {"Metric": "Report Generated At",  "Value": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
    ]

    # Add per-column missing counts
    for col, n in stats["missing_per_col"].items():
        rows.append({"Metric": f"Missing · {col}", "Value": n})

    report_df = pd.DataFrame(rows)
    report_df.to_csv(REPORT_PATH, index=False)
    return report_df


# ─────────────────────────────────────────────────────────────────────────────
def run_pipeline() -> dict:
    """
    End-to-end pipeline.  Called by app.py (and directly for CLI use).
    Returns the stats dict so the dashboard can display it.
    """
    df_raw            = load_raw()
    df_clean, stats   = clean(df_raw)
    df_clean.to_csv(CLEAN_PATH, index=False)
    build_report(stats, df_clean)
    return stats


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    stats = run_pipeline()
    print(json.dumps(stats, indent=2))
    print(f"\n✅  cleaned_data.csv  → {stats['total_clean']} rows")
    print(f"✅  report.csv        → saved")
