"""
analyze_results.py
------------------
Analyzes results from experiment data in /data:
    • Fitts' Law (movement time vs. index of difficulty)
    • Quiz Results (knowledge score)
    • Tracking Test (mouse tracking accuracy) — placeholder
    • Balance Test (stability accuracy) — placeholder

Usage:
    python analyze_results.py <choice>

Choices:
    fitts      - Analyze Fitts' Law data
    quiz       - Analyze Quiz results
    tracking   - Placeholder for tracking data
    balance    - Placeholder for balance data
    all        - Analyze all available types
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# -------------------------------------------------------------------
# Utility helpers
# -------------------------------------------------------------------
def list_csv_files():
    return [f for f in os.listdir(DATA_DIR) if f.endswith(".csv")]

def safe_load_csv(filename):
    try:
        df = pd.read_csv(os.path.join(DATA_DIR, filename))
        return df
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return None

# -------------------------------------------------------------------
# Fitts' Law Analysis
# -------------------------------------------------------------------
def analyze_fitts(filename):
    print(f"\n=== Analyzing {filename} (Fitts' Law) ===")
    df = safe_load_csv(filename)
    if df is None or len(df) < 2:
        print("Not enough data.")
        return

    # Drop invalid rows
    df = df.dropna()
    df = df[(df["Distance (px)"] > 0) & (df["Target Size (px)"] > 0)]

    # Compute Index of Difficulty
    df["Index of Difficulty (bits)"] = np.log2(2 * df["Distance (px)"] / df["Target Size (px)"] + 1)

    # Remove outliers
    q1, q3 = df["Time (ms)"].quantile([0.25, 0.75])
    iqr = q3 - q1
    lower, upper = q1 - 1.5 * iqr, q3 + 1.0 * iqr
    mean_t, std_t = df["Time (ms)"].mean(), df["Time (ms)"].std()
    upper_std = mean_t + 2 * std_t
    df = df[(df["Time (ms)"] >= lower) & (df["Time (ms)"] <= min(upper, upper_std))]

    # Average movement times per ID
    df["ID_rounded"] = df["Index of Difficulty (bits)"].round(2)
    avg_df = df.groupby("ID_rounded")["Time (ms)"].mean().reset_index()
    avg_df.rename(columns={
        "ID_rounded": "Index of Difficulty (bits)",
        "Time (ms)": "Avg Movement Time (ms)"
    }, inplace=True)

    # Regression
    ID, MT = avg_df["Index of Difficulty (bits)"], avg_df["Avg Movement Time (ms)"]
    slope, intercept, r_value, _, _ = linregress(ID, MT)
    r2 = r_value ** 2

    print(f"Equation: MT = {intercept:.2f} + {slope:.2f} * ID")
    print(f"R² = {r2:.3f}")

    # Plot
    plt.figure(figsize=(7, 5))
    plt.scatter(ID, MT, color="blue", label="Data")
    plt.plot(ID, intercept + slope * ID, color="red", label="Fit")
    plt.xlabel("Index of Difficulty  log₂(2A/W + 1)")
    plt.ylabel("Avg Movement Time (ms)")
    plt.title(f"Fitts' Law — {filename}")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plot_path = os.path.join(DATA_DIR, f"{filename.replace('.csv','')}_plot.png")
    plt.savefig(plot_path, dpi=300)
    plt.close()
    print(f"Saved plot to {plot_path}")

# -------------------------------------------------------------------
# Quiz Results Analysis
# -------------------------------------------------------------------
def analyze_quiz():
    quiz_path = os.path.join(DATA_DIR, "quiz_results.csv")
    if not os.path.exists(quiz_path):
        print("\n=== No quiz_results.csv found ===")
        return

    print("\n=== Analyzing Quiz Results ===")
    df = pd.read_csv(quiz_path)
    if "Correct?" not in df.columns:
        print("Invalid format.")
        return

    total = len(df)
    correct = df["Correct?"].sum()
    accuracy = (correct / total) * 100 if total else 0

    print(f"Questions answered: {total}")
    print(f"Correct answers:    {correct}")
    print(f"Accuracy:           {accuracy:.1f}%")

    # Bar chart
    plt.figure(figsize=(5, 4))
    df["Correct?"].value_counts().reindex([1, 0]).fillna(0).plot(
        kind="bar", color=["green", "red"])
    plt.xticks([0, 1], ["Correct", "Incorrect"], rotation=0)
    plt.title("Quiz Results Summary")
    plt.ylabel("Count")
    plt.tight_layout()
    quiz_plot = os.path.join(DATA_DIR, "quiz_results_plot.png")
    plt.savefig(quiz_plot, dpi=300)
    plt.close()
    print(f"Saved plot to {quiz_plot}")


# -------------------------------------------------------------------
# Main Driver
# -------------------------------------------------------------------
if __name__ == "__main__":
    choice = sys.argv[1] if len(sys.argv) > 1 else "all"
    print(f"=== Running Analysis: {choice.upper()} ===")

    if choice in ["fitts", "all"]:
        for f in list_csv_files():
            if f.startswith("fitts_") and f.endswith(".csv"):
                analyze_fitts(f)

    if choice in ["quiz", "all"]:
        analyze_quiz()

    print("\nAnalysis complete. Plots (if any) saved in /data.")
