import tkinter as tk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
from frontend.fitts_test import run_fitts_test
from frontend.tracking_test import run_target_tracking
from frontend.balance_test import run_balance_game
from frontend.typing_test import run_typing_test
from frontend.quiz import run_quiz
from frontend.api_client import register_user
from app.config import Config
import os
import csv
from analyze_results import analyze_fitts, analyze_quiz, list_csv_files


def main():
    root = tk.Tk()
    root.title("Inebriation Learning Tool")
    root.geometry(f"{Config.CANVAS_WIDTH}x{Config.CANVAS_HEIGHT}")
    root.configure(bg=Config.BG_COLOR)

    # --- Initial title and username prompt ---
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

        for w in root.winfo_children():
            w.destroy()

        root.bind("<Return>", lambda e: (root.focus_get().invoke()
                                         if hasattr(root.focus_get(), "invoke") else None))

        tk.Label(root, text=f"Welcome, {username}!", font=Config.FONT_SUBTITLE, bg=Config.BG_COLOR).pack(pady=20)

        # --- Impairment selector ---
        def select_impairment(sim_func, root, user_id):
            level_window = tk.Toplevel(root)
            level_window.title("Select Impairment Level")
            level_window.geometry("300x250")
            level_window.transient(root)

            tk.Label(level_window, text="Choose Impairment Level:", font=Config.FONT_BODY).pack(pady=10)
            levels = [("None", "normal"), ("Mild", "mild"), ("Moderate", "moderate"), ("Severe", "severe")]
            for label, mode in levels:
                tk.Button(
                    level_window,
                    text=label,
                    width=15,
                    command=lambda m=mode: [level_window.destroy(), sim_func(root, user_id, m)],
                    bg="white",
                    relief="flat",
                    font=("Helvetica", 11)
                ).pack(pady=5)

            if sim_func == run_target_tracking:
                tk.Label(
                    level_window,
                    text="⚠ Warning: Severe mode includes rapid movement and flashing.\nMay trigger seizures.",
                    fg=Config.ACCENT_COLOR,
                    font=("Helvetica", 9, "italic"),
                    wraplength=280,
                    justify="left"
                ).pack(pady=(0, 10))

        # --- Simulation buttons ---
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

        # --- Analysis Menu ---
        def open_analysis_menu():
            menu = tk.Toplevel(root)
            menu.title("Select Analysis Type")
            menu.geometry("320x300")
            tk.Label(menu, text="Choose which results to analyze:", font=Config.FONT_BODY).pack(pady=10)

            options = [("Fitts' Law Results", "fitts"),
                       ("Quiz Results", "quiz"),
                       ("All Results", "all")]

            # -------------------- QUIZ ANSWERS WINDOW --------------------
            def show_quiz_answers_from_file(parent):
                data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                         "data", "quiz_results.csv")
                if not os.path.exists(data_path):
                    messagebox.showinfo("No Results", "No quiz results found. Please complete a quiz first.")
                    return

                answers_win = tk.Toplevel(parent)
                answers_win.title("Quiz Answers")
                answers_win.geometry("700x700")

                tk.Label(answers_win, text="Quiz Answers", font=("Helvetica", 14, "bold")).pack(pady=10)
                text_box = ScrolledText(answers_win, wrap="word", font=("Helvetica", 11),
                                        width=80, height=25)
                text_box.pack(padx=10, pady=10, fill="both", expand=True)

                with open(data_path, newline="") as f:
                    reader = csv.DictReader(f)
                    for i, row in enumerate(reader, 1):
                        q_text = row["Question"]
                        your_ans = row["Your Answer"]
                        correct_ans = row["Correct Answer"]
                        correct_flag = row["Correct?"]
                        is_correct = str(correct_flag) == "1"
                        status_text = "Correct" if is_correct else "Incorrect"
                        color_tag = "green_text" if is_correct else "red_text"

                        text_box.insert("end", f"Q{i}. {q_text}\n", "bold")
                        text_box.insert("end", f"Your answer: {your_ans}\n")
                        text_box.insert("end", f"Correct answer: {correct_ans}\n")
                        text_box.insert("end", f"Result: {status_text}\n\n", color_tag)

                text_box.insert("end", "Plots can be generated and saved using the button below.\n")
                text_box.tag_configure("bold", font=("Helvetica", 11, "bold"))
                text_box.tag_configure("green_text", foreground="green")
                text_box.tag_configure("red_text", foreground="red")
                text_box.config(state="disabled")

                # --- Button frame (Close + Generate Graphs) ---
                button_frame = tk.Frame(answers_win, bg=answers_win.cget("bg"))  # dynamically match window background
                button_frame.pack(pady=10, fill="x")

                # --- Close and Generate Graphs buttons (separate, no white area) ---
                def generate_quiz_graphs():
                    plot_path = analyze_quiz()
                    messagebox.showinfo("Graph Generated", f"Quiz plot saved to:\n{plot_path}")

                # Close button
                tk.Button(
                    answers_win,
                    text="Close",
                    command=answers_win.destroy,
                    bg=Config.PRIMARY_COLOR,
                    fg="white",
                    relief="flat",
                    font=("Helvetica", 11, "bold"),
                    width=15
                ).pack(pady=(5, 2))

                # Generate Graphs button
                tk.Button(
                    answers_win,
                    text="Generate Graphs",
                    command=generate_quiz_graphs,
                    bg="#6c757d",
                    fg="white",
                    relief="flat",
                    font=("Helvetica", 11, "bold"),
                    width=15
                ).pack(pady=(2, 10))




            # -------------------- FITTS LAW WINDOW --------------------
            def show_fitts_summary(parent):
                import pandas as pd
                data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

                ordered_modes = ["normal", "mild", "moderate", "severe"]
                files = [f"fitts_{m}.csv" for m in ordered_modes if os.path.exists(os.path.join(data_dir, f"fitts_{m}.csv"))]

                if not files:
                    messagebox.showinfo("No Results", "No Fitts' Law CSV files found.")
                    return

                win = tk.Toplevel(parent)
                win.title("Fitts' Law Results")
                win.geometry("700x700")

                tk.Label(win, text="Fitts' Law Results (ordered by severity)",
                         font=("Helvetica", 14, "bold")).pack(pady=10)

                text_box = ScrolledText(win, wrap="word", font=("Helvetica", 11),
                                        width=80, height=25)
                text_box.pack(padx=10, pady=10, fill="both", expand=True)

                for fname in files:
                    path = os.path.join(data_dir, fname)
                    try:
                        import pandas as pd
                        df = pd.read_csv(path)
                        n = len(df)
                        avg_ms = df["Time (ms)"].mean() if "Time (ms)" in df else float("nan")
                        text_box.insert("end", f"{fname}\n", "bold")
                        text_box.insert("end", f"  Trials: {n}\n")
                        text_box.insert("end", f"  Avg Movement Time: {avg_ms:.2f} ms\n\n")
                    except Exception as e:
                        text_box.insert("end", f"{fname}\n", "bold")
                        text_box.insert("end", f"  Error reading file: {e}\n\n")

                text_box.insert("end", "Plots can be generated and saved using the button below.\n")
                text_box.tag_configure("bold", font=("Helvetica", 11, "bold"))
                text_box.config(state="disabled")

                # --- Button frame (Close + Generate Graphs) ---
                button_frame = tk.Frame(win, bg=Config.BG_COLOR)
                button_frame.pack(pady=10)

                # --- Close and Generate Graphs buttons (separate, no white area) ---
                def generate_fitts_graphs():
                    generated = []
                    for f in files:
                        plot_path = analyze_fitts(f)
                        if plot_path:
                            generated.append(plot_path)
                    msg = "\n".join(generated) if generated else "No files processed."
                    messagebox.showinfo("Graphs Generated", f"Plots saved to:\n{msg}")

                # Close button
                tk.Button(
                    win,
                    text="Close",
                    command=win.destroy,
                    bg=Config.PRIMARY_COLOR,
                    fg="white",
                    relief="flat",
                    font=("Helvetica", 11, "bold"),
                    width=15
                ).pack(pady=(5, 2))

                # Generate Graphs button
                tk.Button(
                    win,
                    text="Generate Graphs",
                    command=generate_fitts_graphs,
                    bg="#6c757d",
                    fg="white",
                    relief="flat",
                    font=("Helvetica", 11, "bold"),
                    width=15
                ).pack(pady=(2, 10))


            # -------------------- MENU HANDLER --------------------
            def run_analysis(choice):
                menu.destroy()
                if choice == "quiz":
                    show_quiz_answers_from_file(root)
                elif choice == "fitts":
                    show_fitts_summary(root)
                else:
                    show_quiz_answers_from_file(root)
                    show_fitts_summary(root)

            for label, key in options:
                tk.Button(menu, text=label, width=25, height=2,
                          command=lambda k=key: run_analysis(k),
                          bg="white", relief="flat", font=("Helvetica", 11)).pack(pady=5)

        # --- Bottom buttons ---
        tk.Button(root, text="Analyze Results", width=25, height=2,
                  command=open_analysis_menu,
                  bg="white", relief="flat", font=("Helvetica", 11)).pack(pady=5)

        tk.Button(root, text="Exit", command=root.destroy, width=25, height=2,
                  bg=Config.PRIMARY_COLOR, fg="white",
                  font=("Helvetica", 11, "bold"), relief="flat").pack(pady=20)

    # --- Start ---
    root.bind("<Return>", lambda e: start_session())
    tk.Button(root, text="Start", command=start_session,
              font=("Helvetica", 12), width=15, height=1,
              bg=Config.PRIMARY_COLOR, fg="white", relief="flat").pack(pady=10)

    root.mainloop()


if __name__ == "__main__":
    main()
