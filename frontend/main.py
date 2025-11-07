import tkinter as tk
import pandas as pd
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
from frontend.tracking_test import run_target_tracking
from frontend.balance_test import run_balance_game
from frontend.typing_test import run_typing_test
from frontend.quiz import run_quiz
from frontend.api_client import get_quiz_csv, register_user
from app.config import Config
import os
import csv
from analyze_results import analyze_quiz, list_csv_files

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

def main():
    # Set up main window
    main_window = tk.Tk()
    main_window.title("Inebriation Learning Tool")
    main_window.geometry(f"{Config.CANVAS_WIDTH}x{Config.CANVAS_HEIGHT}")
    main_window.configure(bg=Config.BG_COLOR)

    # Initial title and username prompt
    tk.Label(main_window, text="Inebriation Learning Tool", font=Config.FONT_TITLE, bg=Config.BG_COLOR).pack(pady=20)
    tk.Label(main_window, text="Enter username to begin:", font=Config.FONT_BODY, bg=Config.BG_COLOR).pack()

    # Username entry
    username_entry = tk.Entry(main_window, font=Config.FONT_BODY)
    username_entry.pack(pady=10)
    username_entry.focus_set()

    # Start session function
    def start_session():
        username = username_entry.get().strip()
        if not username:
            messagebox.showwarning("Missing name", "Please enter a username.")
            return
        # Register user and get user ID
        user_id = register_user(username)
        
        # Get the user's quiz results CSV files
        user_csv_data = get_quiz_csv(user_id)
        # Save the CSV data locally if it exists
        if user_csv_data and "csv_data" in user_csv_data:
            csv_path = os.path.join(DATA_DIR, "quiz_results.csv")
            # Write the CSV string to file
            with open(csv_path, "w", newline="") as csvfile:
                csvfile.write(user_csv_data["csv_data"])
            print(f"Quiz results loaded and saved to {csv_path}")
        else:
            print("No quiz data found for this user.")

        # Clear main window
        for widget in main_window.winfo_children():
            widget.destroy()
            
        # Bind Enter key to focused button
        main_window.bind("<Return>", lambda event: (main_window.focus_get().invoke()
                                         if hasattr(main_window.focus_get(), "invoke") else None))

        # Welcome message
        tk.Label(main_window, text=f"Welcome, {username}!", font=Config.FONT_SUBTITLE, bg=Config.BG_COLOR).pack(pady=20)

        # Impairment selector
        def select_impairment(simulation_function, root_window, user_id_value):
            level_window = tk.Toplevel(root_window)
            level_window.title("Select Impairment Level")
            level_window.geometry("300x250")
            level_window.transient(root_window)

            tk.Label(level_window, text="Choose Impairment Level:", font=Config.FONT_BODY).pack(pady=10)
            impairment_levels = [("None", "normal"), ("Mild", "mild"), ("Moderate", "moderate"), ("Severe", "severe")]
            for label, mode in impairment_levels:
                tk.Button(
                    level_window,
                    text=label,
                    width=15,
                    command=lambda m=mode: [level_window.destroy(), simulation_function(root_window, user_id_value, m)],
                    bg="white",
                    relief="flat",
                    font=("Helvetica", 11)
                ).pack(pady=5)
            if simulation_function == run_target_tracking:
                tk.Label(
                    level_window,
                    text="Warning: Severe mode includes rapid movement and flashing.\nMay trigger seizures.",
                    fg=Config.ACCENT_COLOR,
                    font=("Helvetica", 9, "italic"),
                    wraplength=280,
                    justify="left"
                ).pack(pady=(0, 10))

        # Test buttons
        for button_text, function_reference in [
            ("Target Tracking Test", run_target_tracking),
            ("Balance Game", run_balance_game),
            ("Typing Accuracy Test", run_typing_test)
        ]:
            tk.Button(main_window, text=button_text, width=25, height=2,
                      command=lambda f=function_reference: select_impairment(f, main_window, user_id),
                      bg="white", relief="flat", font=("Helvetica", 11)).pack(pady=5)
        
        # Quiz Button
        tk.Button(main_window, text="Alcohol Knowledge Quiz", width=25, height=2,
                  command=lambda: run_quiz(main_window, user_id),
                  bg="white", relief="flat", font=("Helvetica", 11)).pack(pady=10)

        # Analyze Quiz Results Button
        def analyze_quiz_results():
            data_path = os.path.join(DATA_DIR, "quiz_results.csv")
            if not os.path.exists(data_path):
                messagebox.showinfo("No Results", "No quiz results found. Please complete a quiz first.")
                return

            try:
                df = pd.read_csv(data_path)
                total_questions = len(df)
                correct_answers = df["Correct?"].sum()
                accuracy = (correct_answers / total_questions) * 100 if total_questions > 0 else 0.0

                results_text = (
                    "Analyzing Quiz Results\n"
                    f"Questions answered: {total_questions}\n"
                    f"Correct answers:    {correct_answers}\n"
                    f"Accuracy:           {accuracy:.1f}%"
                )
                messagebox.showinfo("Quiz Results Summary", results_text)
            except Exception as e:
                messagebox.showerror("Error", f"Could not analyze quiz results.\n{e}")

        tk.Button(main_window, text="Analyze Quiz Results", width=25, height=2,
                  command=analyze_quiz_results,
                  bg="white", relief="flat", font=("Helvetica", 11)).pack(pady=5)

        # Exit Button
        tk.Button(main_window, text="Exit", command=main_window.destroy, width=25, height=2,
                  bg=Config.PRIMARY_COLOR, fg="white",
                  font=("Helvetica", 11, "bold"), relief="flat").pack(pady=20)

    # Bind Enter key to start session
    main_window.bind("<Return>", lambda event: start_session())
    tk.Button(main_window, text="Start", command=start_session,
              font=("Helvetica", 12), width=15, height=1,
              bg=Config.PRIMARY_COLOR, fg="white", relief="flat").pack(pady=10)

    main_window.mainloop()


if __name__ == "__main__":
    main()
