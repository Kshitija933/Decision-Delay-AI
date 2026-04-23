"""
DecisionDelay AI — Preprocessing Pipeline v2
=============================================
Steps:
  1. Load raw CSV
  2. Drop duplicates
  3. Clip outliers to [0, 10]
  4. Impute missing values (median per domain)
  5. Normalise use_case casing → title case
  6. Clip delay_severity_raw → [0, 1]  → rename to delay_severity
  7. Engineer 6 derived features (PDF formula names)
  8. One-hot encode use_case → domain_* columns
  9. Drop non-numeric columns (except targets)
 10. Save processed CSV

Run:  python data/preprocessing.py
"""

import numpy as np
import pandas as pd
import os, sys
from pathlib import Path

DATA_DIR     = Path(__file__).resolve().parent
PROJECT_ROOT = DATA_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

from configs.settings import APP_CFG

RAW_PATH  = APP_CFG.raw_path
PROC_PATH = APP_CFG.dataset_path
NUMERIC_COLS = [
    "task_difficulty", "time_to_reward", "past_failure_loops",
    "self_efficacy", "stress_level", "goal_clarity",
    "social_support", "intrinsic_motivation", "habit_strength",
    "distraction_level",
]


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    print(f"[→] Raw shape : {df.shape}")

    # 1. Normalise use_case casing
    if "use_case" in df.columns:
        df["use_case"] = df["use_case"].str.strip().str.title()
        unknown = ~df["use_case"].isin(APP_CFG.use_cases)
        if unknown.any():
            print(f"[!] Unknown use_case values ({unknown.sum()}) → 'Fitness'")
            df.loc[unknown, "use_case"] = "Fitness"

    # 2. Drop exact duplicates
    before = len(df)
    df = df.drop_duplicates()
    print(f"[→] Dropped {before - len(df)} duplicates → {len(df):,} rows")

    # 3. Clip outliers to [0, 10] for all numeric input features
    for col in NUMERIC_COLS:
        if col in df.columns:
            df[col] = df[col].clip(0.0, 10.0)

    # 4. Impute missing values — median per domain group
    if "use_case" in df.columns:
        for col in NUMERIC_COLS:
            if col in df.columns:
                group_median = df.groupby("use_case")[col].transform("median")
                global_median = df[col].median()
                df[col] = df[col].fillna(group_median).fillna(global_median)
    else:
        for col in NUMERIC_COLS:
            if col in df.columns:
                df[col] = df[col].fillna(df[col].median())

    # 5. Clip and rename severity target
    if "delay_severity_raw" in df.columns:
        df["delay_severity"] = df["delay_severity_raw"].clip(0.0, 1.0)
        df = df.drop(columns=["delay_severity_raw"])
    elif "delay_severity" not in df.columns:
        # Derive if missing
        df["delay_severity"] = (
            df.get("task_difficulty", 5) / 10 * 0.25
            + df.get("stress_level",       5) / 10 * 0.20
            + df.get("past_failure_loops", 2) / 10 * 0.20
            - df.get("self_efficacy",      5) / 10 * 0.15
        ).clip(0, 1)

    # 6. Drop respondent_id (not a feature)
    df = df.drop(columns=[c for c in ["respondent_id"] if c in df.columns])

    # 7. Validate delay_cause labels
    valid_causes = set(APP_CFG.delay_causes)
    invalid = ~df["delay_cause"].isin(valid_causes)
    if invalid.any():
        print(f"[!] Invalid delay_cause ({invalid.sum()}) → 'Fear of Failure'")
        df.loc[invalid, "delay_cause"] = "Fear of Failure"

    # 8. Engineer 6 derived features
    df = _engineer(df)

    # 9. One-hot encode use_case
    if "use_case" in df.columns:
        df = pd.get_dummies(df, columns=["use_case"], prefix="domain", dtype=float)

    # 10. Drop any remaining string columns except targets
    targets = {"delay_cause", "delay_severity"}
    bad = [c for c in df.columns if c not in targets and df[c].dtype == object]
    if bad:
        print(f"[!] Dropping non-numeric: {bad}")
        df = df.drop(columns=bad)

    # 11. Final NaN check
    nan_left = df.drop(columns=list(targets & set(df.columns))).isnull().sum().sum()
    if nan_left > 0:
        print(f"[!] {nan_left} NaN remaining — filling with 0")
        df = df.fillna(0)

    print(f"[✓] Processed shape : {df.shape}")
    print(f"    Class distribution:\n{df['delay_cause'].value_counts().to_string()}")
    print(f"    Severity range    : [{df['delay_severity'].min():.3f}, {df['delay_severity'].max():.3f}]")
    return df


def _engineer(df: pd.DataFrame) -> pd.DataFrame:
    """
    6 engineered features — exact PDF formula names.
    All operations are NaN-safe (already imputed at step 4).
    """
    df = df.copy()
    eps = 1e-8  # avoid division by zero

    df["reward_proximity"]   = 1.0 / (df["time_to_reward"] + 1.0)
    df["failure_weight"]     = df["past_failure_loops"] * (10.0 - df["self_efficacy"])
    df["motivation_deficit"] = (10.0 - df["intrinsic_motivation"]) * (10.0 - df["social_support"])
    df["cognitive_load"]     = df["task_difficulty"] + df["stress_level"] + df["distraction_level"]
    df["support_index"]      = df["self_efficacy"] + df["social_support"] + df["habit_strength"]
    df["reward_perception"]  = df["intrinsic_motivation"] / (df["time_to_reward"] + 1.0 + eps)

    # Extra high-signal interactions (v2 additions for higher accuracy)
    df["efficacy_clarity"]   = df["self_efficacy"] * df["goal_clarity"] / 100.0
    df["burnout_index"]      = df["stress_level"] * df["distraction_level"] / 100.0
    df["action_potential"]   = (df["intrinsic_motivation"] + df["habit_strength"]
                                + df["goal_clarity"]) / 30.0
    df["barrier_score"]      = (df["task_difficulty"] + df["past_failure_loops"]
                                + (10 - df["self_efficacy"])) / 30.0

    return df


if __name__ == "__main__":
    os.makedirs(os.path.dirname(PROC_PATH), exist_ok=True)

    if not os.path.exists(RAW_PATH):
        print("[!] Raw data not found. Running raw_data.py...")
        import subprocess
        subprocess.run([sys.executable, str(DATA_DIR / "raw_data.py")])

    df_raw  = pd.read_csv(RAW_PATH)
    df_proc = preprocess(df_raw)
    df_proc.to_csv(PROC_PATH, index=False)
    print(f"\n[✓] Saved → {PROC_PATH}")
    print(f"    Columns ({len(df_proc.columns)}): {df_proc.columns.tolist()}")