import tkinter as tk
from tkinter import messagebox
from frontend.fitts_test import run_fitts_test
from frontend.tracking_test import run_target_tracking
from frontend.balance_test import run_balance_game
from frontend.typing_test import run_typing_test
from frontend.quiz import run_quiz
from frontend.api_client import register_user
from app.config import Config
import subprocess, sys, os


def main():
    root = tk.Tk()
    root.title("Inebriation Learning Tool")

    # main window sizing
    root.geometry(f"{Config.CANVAS_WIDTH}x{Config.CANVAS_HEIGHT}")

    tk.Label(root, text="Inebriation Learning Tool", font=("Helvetica", 18, "bold")).pack(pady=20)
    tk.Label(root, text="Enter username to begin:", font=("Helvetica", 12)).pack()

    entry = tk.Entry(root, font=("Helvetica", 12))
    entry.pack(pady=10)

    def start_session():
        username = entry.get().strip()
        if not username:
            messagebox.showwarning("Missing name", "Please enter a username.")
            return
        user_id = register_user(username)

        # Clear start widgets and show buttons
        for w in root.winfo_children():
            w.destroy()

        tk.Label(root, text=f"Welcome, {username}!", font=("Helvetica", 16, "bold")).pack(pady=20)

        # --- Simulation Buttons with Impairment Level Selection ---
        def select_impairment(sim_func, root, user_id):
            """Popup window to choose impairment level before running a simulation."""
            level_window = tk.Toplevel(root)
            level_window.title("Select Impairment Level")
            level_window.geometry("300x250")

            tk.Label(level_window, text="Choose Impairment Level:", font=("Helvetica", 12, "bold")).pack(pady=10)
            levels = [("None", "normal"), ("Mild", "mild"), ("Moderate", "moderate"), ("Severe", "severe")]

            for label, mode in levels:
                tk.Button(
                    level_window,
                    text=label,
                    width=15,
                    command=lambda m=mode: launch_simulation(sim_func, root, user_id, m, level_window)
                ).pack(pady=5)

        def launch_simulation(sim_func, root, user_id, mode, level_window):
            level_window.destroy()
            sim_func(root, user_id, mode)

        # --- Add Simulation Buttons ---
        tk.Button(root, text="Fitts' Law Test",
                  command=lambda: select_impairment(run_fitts_test, root, user_id),
                  width=25, height=2).pack(pady=5)

        tk.Button(root, text="Target Tracking Test",
                  command=lambda: select_impairment(run_target_tracking, root, user_id),
                  width=25, height=2).pack(pady=5)

        tk.Button(root, text="Balance Game",
                  command=lambda: select_impairment(run_balance_game, root, user_id),
                  width=25, height=2).pack(pady=5)

        tk.Button(root, text="Typing Accuracy Test",
                  command=lambda: select_impairment(run_typing_test, root, user_id),
                  width=25, height=2).pack(pady=5)
        # ------------------

        tk.Button(root, text="Alcohol Knowledge Quiz",
                  command=lambda: run_quiz(root, user_id),
                  width=25, height=2).pack(pady=5)

        # =========================================================
        # Analyze Results (multi-choice window)
        # =========================================================
        def open_analysis_menu():
            """Popup with choices for what type of analysis to run."""
            menu = tk.Toplevel(root)
            menu.title("Select Analysis Type")
            menu.geometry("320x300")

            tk.Label(menu, text="Choose which results to analyze:", font=("Helvetica", 12, "bold")).pack(pady=10)

            options = [
                ("Fitts' Law Results", "fitts"),
                ("Quiz Results", "quiz"),
                ("All Results", "all")
            ]

            def run_analysis(choice):
                menu.destroy()
                script = os.path.join(os.path.dirname(os.path.dirname(__file__)), "analyze_results.py")
                subprocess.run([sys.executable, script, choice], check=False)

            for label, key in options:
                tk.Button(menu, text=label, width=25, height=2,
                          command=lambda k=key: run_analysis(k)).pack(pady=5)

        tk.Button(root, text="Analyze Results",
                  command=open_analysis_menu, width=25, height=2).pack(pady=5)
        # =========================================================

        tk.Button(root, text="Exit", command=root.destroy, width=25, height=2).pack(pady=20)

    tk.Button(root, text="Start", command=start_session, font=("Helvetica", 12), width=15, height=1).pack(pady=10)

    root.mainloop()


if __name__ == "__main__":
    main()
