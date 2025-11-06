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
    entry.focus_set()

    # ---------------------------------------------------------------
    # Helper: Make buttons focusable and triggerable with Enter
    # ---------------------------------------------------------------
    def make_button_accessible(button):
        button.bind("<Return>", lambda event: button.invoke())
        button.configure(takefocus=True)

    # ---------------------------------------------------------------
    # Start session setup
    # ---------------------------------------------------------------
    def start_session():
        username = entry.get().strip()
        if not username:
            messagebox.showwarning("Missing name", "Please enter a username.")
            return

        # Unbind global Enter to prevent TclError after widgets are destroyed
        root.unbind("<Return>")

        user_id = register_user(username)

        # Clear login widgets
        for w in root.winfo_children():
            w.destroy()

        tk.Label(root, text=f"Welcome, {username}!", font=("Helvetica", 16, "bold")).pack(pady=20)

        # ---------------------------------------------------------------
        # Impairment selection dialog
        # ---------------------------------------------------------------
        def select_impairment(sim_func, root, user_id):
            """Popup window to choose impairment level before running a simulation."""
            level_window = tk.Toplevel(root)
            level_window.title("Select Impairment Level")

            # --- Center within parent window ---
            root.update_idletasks()
            parent_x = root.winfo_x()
            parent_y = root.winfo_y()
            parent_w = root.winfo_width()
            parent_h = root.winfo_height()

            width, height = 320, 280
            x = parent_x + (parent_w // 2) - (width // 2)
            y = parent_y + (parent_h // 2) - (height // 2)
            level_window.geometry(f"{width}x{height}+{x}+{y}")
            level_window.transient(root)
            level_window.grab_set()  # Modal dialog

            tk.Label(level_window, text="Choose Impairment Level:", font=("Helvetica", 12, "bold")).pack(pady=10)
            levels = [("None", "normal"), ("Mild", "mild"), ("Moderate", "moderate"), ("Severe", "severe")]

            for label, mode in levels:
                btn = tk.Button(
                    level_window,
                    text=label,
                    width=15,
                    command=lambda m=mode: launch_simulation(sim_func, root, user_id, m, level_window)
                )
                btn.pack(pady=5)
                make_button_accessible(btn)

                # --- Photosensitive warning only for Target Tracking (severe) ---
                if mode == "severe" and sim_func == run_target_tracking:
                    tk.Label(
                        level_window,
                        text="⚠ Warning: This mode includes rapid movement and flashing.\n"
                             "It may trigger seizures in photosensitive individuals.",
                        fg="red",
                        font=("Helvetica", 9, "italic"),
                        wraplength=280,
                        justify="left"
                    ).pack(pady=(0, 10))

        def launch_simulation(sim_func, root, user_id, mode, level_window):
            level_window.destroy()
            sim_func(root, user_id, mode)

        # ---------------------------------------------------------------
        # Button factory
        # ---------------------------------------------------------------
        def create_button(label, command):
            btn = tk.Button(root, text=label, command=command, width=25, height=2)
            btn.pack(pady=5)
            make_button_accessible(btn)
            return btn

        # ---------------------------------------------------------------
        # Simulation/Test Buttons
        # ---------------------------------------------------------------
        create_button("Fitts' Law Test", lambda: select_impairment(run_fitts_test, root, user_id))
        create_button("Target Tracking Test", lambda: select_impairment(run_target_tracking, root, user_id))
        create_button("Balance Game", lambda: select_impairment(run_balance_game, root, user_id))
        create_button("Typing Accuracy Test", lambda: select_impairment(run_typing_test, root, user_id))
        create_button("Alcohol Knowledge Quiz", lambda: run_quiz(root, user_id))

        # ---------------------------------------------------------------
        # Results analysis menu
        # ---------------------------------------------------------------
        def open_analysis_menu():
            menu = tk.Toplevel(root)
            menu.title("Select Analysis Type")

            # --- Center within parent window ---
            root.update_idletasks()
            px, py = root.winfo_x(), root.winfo_y()
            pw, ph = root.winfo_width(), root.winfo_height()
            mw, mh = 320, 300
            x = px + (pw // 2) - (mw // 2)
            y = py + (ph // 2) - (mh // 2)
            menu.geometry(f"{mw}x{mh}+{x}+{y}")
            menu.transient(root)
            menu.grab_set()

            tk.Label(menu, text="Choose which results to analyze:", font=("Helvetica", 12, "bold")).pack(pady=10)
            options = [("Fitts' Law Results", "fitts"), ("Quiz Results", "quiz"), ("All Results", "all")]

            def run_analysis(choice):
                menu.destroy()
                script = os.path.join(os.path.dirname(os.path.dirname(__file__)), "analyze_results.py")
                subprocess.run([sys.executable, script, choice], check=False)

            for label, key in options:
                btn = tk.Button(menu, text=label, width=25, height=2,
                                command=lambda k=key: run_analysis(k))
                btn.pack(pady=5)
                make_button_accessible(btn)

        create_button("Analyze Results", open_analysis_menu)
        create_button("Exit", root.destroy)

    # ---------------------------------------------------------------
    # Main screen: Start session controls
    # ---------------------------------------------------------------
    start_button = tk.Button(root, text="Start", command=start_session, font=("Helvetica", 12), width=15, height=1)
    start_button.pack(pady=10)

    # Global Enter binding — triggers Start from anywhere
    def on_enter_key(event):
        start_session()

    root.bind("<Return>", on_enter_key)

    root.mainloop()


if __name__ == "__main__":
    main()
