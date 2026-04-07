"""
DecisionDelay AI — Exploratory Data Analysis (EDA)
====================================================
Reads raw data and produces comprehensive analysis plots + statistics.

Run from project root OR inside data/ folder:
    python data/eda.py
    python eda.py

Outputs saved to: reports/eda/
  - 01_class_distribution.png
  - 02_feature_distributions.png
  - 03_correlation_heatmap.png
  - 04_features_by_cause.png
  - 05_severity_by_cause.png
  - 06_cause_by_domain.png
  - 07_missing_values.png
  - 08_outlier_analysis.png
  - eda_summary.txt
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
import sys
import warnings
from pathlib import Path
warnings.filterwarnings("ignore")

# ── Robust path setup ──────────────────────────────────────────────────────────
DATA_DIR     = Path(__file__).resolve().parent          # .../project/data/
PROJECT_ROOT = DATA_DIR.parent                          # .../project/
RAW_PATH     = DATA_DIR / "raw" / "decision_delay_raw.csv"
EDA_DIR      = PROJECT_ROOT / "reports" / "eda"
EDA_DIR.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(PROJECT_ROOT))
# ───────────────────────────────────────────────────────────────────────────────

PALETTE = {
    "Fear of Failure":           "#F43F5E",
    "Overwhelm / Complexity":    "#F59E0B",
    "Lack of Immediate Reward":  "#1A56DB",
    "Past Failure Loop":         "#7C3AED",
    "Perfectionism":             "#FB8500",
    "Decision Fatigue":          "#0EA5E9",
}
CAUSES = list(PALETTE.keys())
NUMERIC_COLS = [
    "task_difficulty", "time_to_reward", "past_failure_loops",
    "self_efficacy", "stress_level", "goal_clarity",
    "social_support", "intrinsic_motivation", "habit_strength",
    "distraction_level",
]
sns.set_theme(style="whitegrid", font="DejaVu Sans")


def load():
    if not RAW_PATH.exists():
        print(f"[!] Raw data not found at {RAW_PATH}")
        print("    Run: python raw_data.py  (inside data/ folder) first")
        sys.exit(1)
    df = pd.read_csv(RAW_PATH)
    print(f"[✓] Loaded raw data: {df.shape}")
    return df


# ── PLOT 1: Class Distribution ────────────────────────────────
def plot_class_distribution(df):
    counts  = df["delay_cause"].value_counts()
    colors  = [PALETTE.get(c, "#64748B") for c in counts.index]
    fig, ax = plt.subplots(figsize=(12, 5))
    bars = ax.barh(counts.index, counts.values, color=colors,
                   edgecolor="white", linewidth=0.5)
    for bar, val in zip(bars, counts.values):
        ax.text(val + 30, bar.get_y() + bar.get_height() / 2,
                f"{val:,}  ({val/len(df)*100:.1f}%)", va="center", fontsize=10)
    ax.set_xlabel("Count", fontsize=11)
    ax.set_title("Delay Cause Class Distribution", fontsize=14, fontweight="bold")
    ax.set_xlim(0, counts.max() * 1.22)
    plt.tight_layout()
    path = EDA_DIR / "01_class_distribution.png"
    plt.savefig(path, dpi=150, bbox_inches="tight"); plt.close()
    print(f"[✓] {path}")


# ── PLOT 2: Feature Distributions ────────────────────────────
def plot_feature_distributions(df):
    fig, axes = plt.subplots(3, 4, figsize=(18, 12))
    axes = axes.flatten()
    palette_list = sns.color_palette("Set2", 12)
    for i, col in enumerate(NUMERIC_COLS):
        axes[i].hist(df[col].dropna(), bins=35,
                     color=palette_list[i], edgecolor="white", alpha=0.85)
        axes[i].axvline(df[col].mean(), color="crimson", linestyle="--",
                        linewidth=1.5, label=f"Mean={df[col].mean():.2f}")
        axes[i].axvline(df[col].median(), color="navy", linestyle=":",
                        linewidth=1.5, label=f"Median={df[col].median():.2f}")
        axes[i].set_title(col.replace("_", " ").title(), fontsize=10, fontweight="bold")
        axes[i].legend(fontsize=7)
        axes[i].set_xlabel("Value"); axes[i].set_ylabel("Frequency")
    for j in range(len(NUMERIC_COLS), len(axes)):
        axes[j].set_visible(False)
    fig.suptitle("Feature Distributions — Raw Data", fontsize=14,
                 fontweight="bold", y=1.01)
    plt.tight_layout()
    path = EDA_DIR / "02_feature_distributions.png"
    plt.savefig(path, dpi=150, bbox_inches="tight"); plt.close()
    print(f"[✓] {path}")


# ── PLOT 3: Correlation Heatmap ───────────────────────────────
def plot_correlation(df):
    corr = df[NUMERIC_COLS + ["delay_severity_raw"]].corr()
    mask = np.triu(np.ones_like(corr, dtype=bool))
    fig, ax = plt.subplots(figsize=(13, 10))
    sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap="RdBu_r",
                center=0, square=True, ax=ax, cbar_kws={"shrink": 0.8},
                annot_kws={"size": 9})
    ax.set_title("Feature Correlation Matrix", fontsize=14, fontweight="bold")
    plt.tight_layout()
    path = EDA_DIR / "03_correlation_heatmap.png"
    plt.savefig(path, dpi=150, bbox_inches="tight"); plt.close()
    print(f"[✓] {path}")


# ── PLOT 4: Key Features by Delay Cause ──────────────────────
def plot_features_by_cause(df):
    key_feats = ["task_difficulty", "time_to_reward", "past_failure_loops",
                 "self_efficacy", "stress_level", "delay_severity_raw"]
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    for ax, feat in zip(axes.flatten(), key_feats):
        data   = [df[df["delay_cause"] == c][feat].dropna().values for c in CAUSES]
        colors = list(PALETTE.values())
        bp = ax.boxplot(data, patch_artist=True,
                        labels=[c.replace(" / ", "/\n")[:18] for c in CAUSES])
        for patch, color in zip(bp["boxes"], colors):
            patch.set_facecolor(color); patch.set_alpha(0.75)
        ax.set_title(feat.replace("_", " ").title(), fontsize=11, fontweight="bold")
        ax.tick_params(axis="x", labelsize=7)
    fig.suptitle("Key Features by Delay Cause", fontsize=14, fontweight="bold")
    plt.tight_layout()
    path = EDA_DIR / "04_features_by_cause.png"
    plt.savefig(path, dpi=150, bbox_inches="tight"); plt.close()
    print(f"[✓] {path}")


# ── PLOT 5: Severity Distribution by Cause ───────────────────
def plot_severity_by_cause(df):
    fig, ax = plt.subplots(figsize=(12, 6))
    for cause, color in PALETTE.items():
        sub = df[df["delay_cause"] == cause]["delay_severity_raw"].dropna().clip(0, 1)
        if len(sub) > 10:
            sns.kdeplot(sub, ax=ax, label=cause, color=color,
                        fill=True, alpha=0.25, linewidth=2)
    ax.set_xlabel("Delay Severity (raw)", fontsize=11)
    ax.set_title("Delay Severity Distribution by Cause", fontsize=14, fontweight="bold")
    ax.legend(fontsize=9); ax.set_xlim(0, 1)
    plt.tight_layout()
    path = EDA_DIR / "05_severity_by_cause.png"
    plt.savefig(path, dpi=150, bbox_inches="tight"); plt.close()
    print(f"[✓] {path}")


# ── PLOT 6: Cause by Domain ───────────────────────────────────
def plot_cause_by_domain(df):
    domains = ["Fitness", "Studying", "Career Choices"]
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    for ax, dom in zip(axes, domains):
        sub = df[df["use_case"].str.lower() == dom.lower()]
        counts = sub["delay_cause"].value_counts()
        colors = [PALETTE.get(c, "#64748B") for c in counts.index]
        ax.pie(counts.values, labels=counts.index, autopct="%1.1f%%",
               startangle=90, colors=colors, textprops={"fontsize": 8})
        ax.set_title(f"{dom}\n(n={len(sub):,})", fontsize=11, fontweight="bold")
    fig.suptitle("Delay Cause Distribution by Domain", fontsize=14, fontweight="bold")
    plt.tight_layout()
    path = EDA_DIR / "06_cause_by_domain.png"
    plt.savefig(path, dpi=150, bbox_inches="tight"); plt.close()
    print(f"[✓] {path}")


# ── PLOT 7: Missing Values ────────────────────────────────────
def plot_missing_values(df):
    miss     = df[NUMERIC_COLS].isnull().sum().sort_values(ascending=False)
    miss_pct = (miss / len(df) * 100).round(2)
    fig, ax  = plt.subplots(figsize=(12, 5))
    bars = ax.bar(miss.index, miss_pct.values, color="#F43F5E", alpha=0.8, edgecolor="white")
    for bar, val in zip(bars, miss_pct.values):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 0.05,
                f"{val:.1f}%", ha="center", fontsize=9)
    ax.set_ylabel("Missing (%)", fontsize=11)
    ax.set_title("Missing Values per Feature (Raw Data)", fontsize=14, fontweight="bold")
    ax.set_ylim(0, max(miss_pct.max() * 1.3, 1))
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    path = EDA_DIR / "07_missing_values.png"
    plt.savefig(path, dpi=150, bbox_inches="tight"); plt.close()
    print(f"[✓] {path}")


# ── PLOT 8: Outlier Analysis ──────────────────────────────────
def plot_outlier_analysis(df):
    fig, ax = plt.subplots(figsize=(14, 6))
    data_clipped = [df[c].dropna().clip(-2, 13).values for c in NUMERIC_COLS]
    bp = ax.boxplot(data_clipped, patch_artist=True,
                    labels=[c.replace("_", "\n")[:14] for c in NUMERIC_COLS])
    palette = sns.color_palette("Set2", len(NUMERIC_COLS))
    for patch, color in zip(bp["boxes"], palette):
        patch.set_facecolor(color); patch.set_alpha(0.75)
    ax.axhline(0,  color="red",   linestyle="--", linewidth=1, alpha=0.6, label="Min valid (0)")
    ax.axhline(10, color="green", linestyle="--", linewidth=1, alpha=0.6, label="Max valid (10)")
    ax.set_title("Outlier Analysis — Feature Ranges (Raw Data)",
                 fontsize=14, fontweight="bold")
    ax.legend(fontsize=9)
    plt.tight_layout()
    path = EDA_DIR / "08_outlier_analysis.png"
    plt.savefig(path, dpi=150, bbox_inches="tight"); plt.close()
    print(f"[✓] {path}")


# ── Summary text ──────────────────────────────────────────────
def save_summary(df):
    lines = [
        "=" * 60,
        "  DecisionDelay AI — EDA Summary",
        "=" * 60,
        f"\nDataset shape    : {df.shape}",
        f"Total rows       : {len(df):,}",
        f"Duplicate rows   : {df.duplicated().sum():,}",
        f"Total missing    : {df.isnull().sum().sum():,}",
        f"\nClass distribution:\n{df['delay_cause'].value_counts().to_string()}",
        f"\nDomain distribution:\n{df['use_case'].value_counts().to_string()}",
        f"\nDescriptive statistics:\n{df[NUMERIC_COLS].describe().round(3).to_string()}",
        f"\nMissing per column:\n{df[NUMERIC_COLS].isnull().sum().to_string()}",
        "\n" + "=" * 60,
    ]
    path = EDA_DIR / "eda_summary.txt"
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[✓] {path}")


def main():
    print("\n" + "=" * 60)
    print("  DecisionDelay AI — EDA")
    print("=" * 60)
    df = load()
    print(f"  Generating 8 EDA plots → {EDA_DIR}\n")
    plot_class_distribution(df)
    plot_feature_distributions(df)
    plot_correlation(df)
    plot_features_by_cause(df)
    plot_severity_by_cause(df)
    plot_cause_by_domain(df)
    plot_missing_values(df)
    plot_outlier_analysis(df)
    save_summary(df)
    print("\n[✓] EDA complete!")


if __name__ == "__main__":
    main()