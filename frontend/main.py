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
    root.geometry(f"{Config.CANVAS_WIDTH}x{Config.CANVAS_HEIGHT}")
    root.configure(bg=Config.BG_COLOR)

    # --- Username entry screen ---
    tk.Label(root, text="Inebriation Learning Tool", font=Config.FONT_TITLE, bg=Config.BG_COLOR).pack(pady=20)
    tk.Label(root, text="Enter username to begin:", font=Config.FONT_BODY, bg=Config.BG_COLOR).pack()

    entry = tk.Entry(root, font=Config.FONT_BODY)
    entry.pack(pady=10)
    entry.focus_set()

    def start_session():
        username = entry.get().strip()
        if not username:
            messagebox.showwarning("Missing name", "Please enter a username.")
            return
        user_id = register_user(username)

        # Clear start widgets
        for w in root.winfo_children():
            w.destroy()

        # --- Rebind Enter to activate focused button ---
        root.bind("<Return>", lambda event: root.focus_get().invoke() if hasattr(root.focus_get(), "invoke") else None)

        # --- Main menu UI ---
        tk.Label(root, text=f"Welcome, {username}!", font=Config.FONT_SUBTITLE, bg=Config.BG_COLOR).pack(pady=20)

        def select_impairment(sim_func, root, user_id):
            """Popup to choose impairment level before running a simulation."""
            level_window = tk.Toplevel(root)
            level_window.title("Select Impairment Level")
            level_window.geometry("300x250")
            level_window.transient(root)  # keep on top of parent

            tk.Label(level_window, text="Choose Impairment Level:",
                    font=Config.FONT_BODY).pack(pady=10)

            levels = [("None", "normal"), ("Mild", "mild"),
                    ("Moderate", "moderate"), ("Severe", "severe")]
            buttons = []

            for idx, (label, mode) in enumerate(levels, start=1):
                btn = tk.Button(
                    level_window,
                    text=label,
                    width=15,
                    command=lambda m=mode: launch_simulation(sim_func, root, user_id, m, level_window),
                    bg="white",
                    relief="flat",
                    font=("Helvetica", 11),
                    takefocus=True
                )
                btn.pack(pady=5)
                buttons.append(btn)

                # Add photosensitivity warning under severe option
                if label == "Severe" and sim_func == run_target_tracking:
                    tk.Label(
                        level_window,
                        text="⚠ Warning: This mode includes rapid movement and flashing.\n"
                            "It may trigger seizures in photosensitive individuals.",
                        fg=Config.ACCENT_COLOR,
                        font=("Helvetica", 9, "italic"),
                        wraplength=280,
                        justify="left"
                    ).pack(pady=(0, 10))

            # --- Keyboard shortcuts inside this window ---
            # Enter triggers the focused button (if invokable)
            level_window.bind(
                "<Return>",
                lambda e: (level_window.focus_get().invoke()
                        if hasattr(level_window.focus_get(), "invoke") else None)
            )
            # Escape closes the dialog
            level_window.bind("<Escape>", lambda e: level_window.destroy())

            # Focus first button so Enter works immediately
            if buttons:
                buttons[0].focus_set()


        def launch_simulation(sim_func, root, user_id, mode, level_window):
            level_window.destroy()
            sim_func(root, user_id, mode)

        # Simulation buttons
        for text, func in [
            ("Fitts' Law Test", run_fitts_test),
            ("Target Tracking Test", run_target_tracking),
            ("Balance Game", run_balance_game),
            ("Typing Accuracy Test", run_typing_test)
        ]:
            tk.Button(root, text=text, width=25, height=2,
                      command=lambda f=func: select_impairment(f, root, user_id),
                      bg="white", relief="flat", font=("Helvetica", 11)).pack(pady=5)

        tk.Button(root, text="Alcohol Knowledge Quiz", width=25, height=2,
                  command=lambda: run_quiz(root, user_id),
                  bg="white", relief="flat", font=("Helvetica", 11)).pack(pady=10)

        def open_analysis_menu():
            menu = tk.Toplevel(root)
            menu.title("Select Analysis Type")
            menu.geometry("320x300")
            tk.Label(menu, text="Choose which results to analyze:", font=Config.FONT_BODY).pack(pady=10)
            options = [("Fitts' Law Results", "fitts"), ("Quiz Results", "quiz"), ("All Results", "all")]

            def run_analysis(choice):
                menu.destroy()
                script = os.path.join(os.path.dirname(os.path.dirname(__file__)), "analyze_results.py")
                subprocess.run([sys.executable, script, choice], check=False)

            for label, key in options:
                tk.Button(menu, text=label, width=25, height=2,
                          command=lambda k=key: run_analysis(k),
                          bg="white", relief="flat", font=("Helvetica", 11)).pack(pady=5)

        tk.Button(root, text="Analyze Results", width=25, height=2,
                  command=open_analysis_menu,
                  bg="white", relief="flat", font=("Helvetica", 11)).pack(pady=5)
        tk.Button(root, text="Exit", command=root.destroy, width=25, height=2,
                  bg=Config.PRIMARY_COLOR, fg="white", font=("Helvetica", 11, "bold"), relief="flat").pack(pady=20)

    # --- Bind Enter only for username entry ---
    root.bind("<Return>", lambda event: start_session())

    tk.Button(root, text="Start", command=start_session,
              font=("Helvetica", 12), width=15, height=1,
              bg=Config.PRIMARY_COLOR, fg="white", relief="flat").pack(pady=10)

    root.mainloop()



if __name__ == "__main__":
    main()
