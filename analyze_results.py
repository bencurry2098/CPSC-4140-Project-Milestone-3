"""
analyze_results.py
------------------
Creates plots for Fitts' Law and Quiz results.
Plots are saved under /data and their paths are returned so the GUI can show them.
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)


def list_csv_files():
    return [f for f in os.listdir(DATA_DIR) if f.endswith(".csv")]


def safe_load_csv(filename):
    try:
        return pd.read_csv(os.path.join(DATA_DIR, filename))
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return None

# -------------------------------------------------------------------
# Quiz Results Analysis
# -------------------------------------------------------------------
def analyze_quiz():
    quiz_path = os.path.join(DATA_DIR, "quiz_results.csv")
    if not os.path.exists(quiz_path):
        print("\n=== No quiz_results.csv found ===")
        return None

    df = pd.read_csv(quiz_path)
    if "Correct?" not in df.columns:
        print("Invalid format.")
        return None

    total = len(df)
    correct = df["Correct?"].sum()
    accuracy = (correct / total) * 100 if total else 0

    print(f"\n=== Analyzing Quiz Results ===")
    print(f"Questions answered: {total}")
    print(f"Correct answers:    {correct}")
    print(f"Accuracy:           {accuracy:.1f}%")

    fig, ax = plt.subplots(figsize=(4, 3))
    df["Correct?"].value_counts().reindex([1, 0]).fillna(0).plot(
        kind="bar", color=["green", "red"], ax=ax)
    ax.set_xticklabels(["Correct", "Incorrect"], rotation=0)
    ax.set_ylabel("Count")
    ax.set_title(f"Quiz Results (Accuracy: {accuracy:.1f}%)")
    plt.tight_layout()

    plot_path = os.path.join(DATA_DIR, "quiz_results_plot.png")
    plt.savefig(plot_path, dpi=300)
    plt.close(fig)
    print(f"Saved plot to {plot_path}")
    return plot_path


if __name__ == "__main__":
    choice = sys.argv[1] if len(sys.argv) > 1 else "all"
    print(f"=== Running Analysis: {choice.upper()} ===")

    if choice in ["quiz", "all"]:
        analyze_quiz()

    print("\nAnalysis complete. Saved in /data.")
