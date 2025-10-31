"""
analyze_results.py
------------------
Analyzes data from the Fitts' Law experiment and visualizes how movement time (MT)
depends on the index of difficulty (ID).

Enhancements:
    • Reads data directly from /data/fitts_normal.csv or /data/fitts_simulated.csv.
    • Removes outliers using IQR and standard deviation.
    • Averages trials with the same Index of Difficulty.
    • Saves the regression plot to /data/fitts_plot.png.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress
import os

# -------------------------------------------------------------------
# Step 1: Locate and load experimental results
# -------------------------------------------------------------------
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# You can switch to "fitts_simulated.csv" if you want to analyze the simulated dataset.
csv_file = os.path.join(DATA_DIR, "fitts_normal.csv")

if not os.path.exists(csv_file):
    raise FileNotFoundError(f"{csv_file} not found. Run a Fitts' Law test first.")

data = pd.read_csv(csv_file)

# Drop invalid or missing rows
data = data.dropna()
data = data[(data["Distance (px)"] > 0) & (data["Target Size (px)"] > 0)]

print("Loaded data sample:")
print(data.head(), "\n")

# -------------------------------------------------------------------
# Step 2: Compute Index of Difficulty (ID)
# -------------------------------------------------------------------
data["Index of Difficulty (bits)"] = np.log2(2 * data["Distance (px)"] / data["Target Size (px)"] + 1)

# -------------------------------------------------------------------
# Step 3: Remove statistical outliers
# -------------------------------------------------------------------
q1 = data["Time (ms)"].quantile(0.25)
q3 = data["Time (ms)"].quantile(0.75)
iqr = q3 - q1
lower_bound = q1 - 1.5 * iqr
upper_bound = q3 + 1.0 * iqr

mean_time = data["Time (ms)"].mean()
std_time = data["Time (ms)"].std()
upper_std = mean_time + 2 * std_time

filtered_data = data[
    (data["Time (ms)"] >= lower_bound) &
    (data["Time (ms)"] <= min(upper_bound, upper_std))
]

removed = len(data) - len(filtered_data)
print(f"Removed {removed} outlier(s) using IQR/std filtering.\n")
data = filtered_data

# -------------------------------------------------------------------
# Step 4: Average movement times per unique ID
# -------------------------------------------------------------------
data["ID_rounded"] = data["Index of Difficulty (bits)"].round(2)
avg_data = data.groupby("ID_rounded")["Time (ms)"].mean().reset_index()
avg_data.rename(columns={
    "ID_rounded": "Index of Difficulty (bits)",
    "Time (ms)": "Avg Movement Time (ms)"
}, inplace=True)

# -------------------------------------------------------------------
# Step 5: Linear regression on averaged data
# -------------------------------------------------------------------
ID = avg_data["Index of Difficulty (bits)"]
MT = avg_data["Avg Movement Time (ms)"]

slope, intercept, r_value, p_value, std_err = linregress(ID, MT)
r_squared = r_value ** 2

# -------------------------------------------------------------------
# Step 6: Display regression results
# -------------------------------------------------------------------
print("Fitts' Law Regression Results")
print("-----------------------------")
print(f"Equation:  MT = {intercept:.2f} + {slope:.2f} * ID")
print(f"a (intercept): {intercept:.2f} ms")
print(f"b (slope): {slope:.2f} ms/bit")
print(f"R² (fit quality): {r_squared:.4f}\n")

if r_squared >= 0.8:
    print("Strong linear relationship: results strongly support Fitts’ Law.")
elif r_squared >= 0.5:
    print("Moderate correlation: results partially support Fitts’ Law.")
else:
    print("Weak correlation: data shows remaining variance or inconsistency.")
print()

# -------------------------------------------------------------------
# Step 7: Plot results
# -------------------------------------------------------------------
plt.figure(figsize=(8, 6))
plt.scatter(ID, MT, color="blue", label="Averaged Trials")
plt.plot(ID, intercept + slope * ID, color="red", label="Linear Fit")

plt.text(min(ID), max(MT)*0.95,
         f"MT = {intercept:.1f} + {slope:.1f} * ID\nR² = {r_squared:.2f}",
         color="red", fontsize=10)

plt.xlabel("Index of Difficulty  log₂(2A/W + 1)")
plt.ylabel("Average Movement Time (ms)")
plt.title("Fitts' Law: Relationship Between Movement Time and Task Difficulty")
plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
plt.grid(True)
plt.tight_layout()

plot_path = os.path.join(DATA_DIR, "fitts_plot.png")
plt.savefig(plot_path, dpi=300)
plt.show()

print(f"Plot saved to: {plot_path}")
