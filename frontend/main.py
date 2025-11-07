import tkinter as tk
import pandas as pd
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

            # Impairment level buttons
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
            # Warning for severe mode in target tracking
            if simulation_function == run_target_tracking:
                tk.Label(
                    level_window,
                    text="Warning: Severe mode includes rapid movement and flashing.\nMay trigger seizures.",
                    fg=Config.ACCENT_COLOR,
                    font=("Helvetica", 9, "italic"),
                    wraplength=280,
                    justify="left"
                ).pack(pady=(0, 10))

        # For each test button, create a button with the appropriate command
        for button_text, function_reference in [
            ("Fitts' Law Test", run_fitts_test),
            ("Target Tracking Test", run_target_tracking),
            ("Balance Game", run_balance_game),
            ("Typing Accuracy Test", run_typing_test)
        ]:
            # Call the impairment selector with the test function
            tk.Button(main_window, text=button_text, width=25, height=2,
                      command=lambda f=function_reference: select_impairment(f, main_window, user_id),
                      bg="white", relief="flat", font=("Helvetica", 11)).pack(pady=5)
        
        # Quiz Button
        tk.Button(main_window, text="Alcohol Knowledge Quiz", width=25, height=2,
                  command=lambda: run_quiz(main_window, user_id),
                  bg="white", relief="flat", font=("Helvetica", 11)).pack(pady=10)

        # Analysis Menu
        def open_analysis_menu():
            analysis_menu = tk.Toplevel(main_window)
            analysis_menu.title("Select Analysis Type")
            analysis_menu.geometry("320x300")
            tk.Label(analysis_menu, text="Choose which results to analyze:", font=Config.FONT_BODY).pack(pady=10)

            analysis_options = [("Fitts' Law Results", "fitts"),
                                ("Quiz Results", "quiz"),
                                ("All Results", "all")]

            # Quiz answers window
            def show_quiz_answers_from_file(parent_window):
                data_path = os.path.join(DATA_DIR, "quiz_results.csv")
                if not os.path.exists(DATA_DIR) or not os.path.isfile(data_path):
                    messagebox.showinfo("No Results", "No quiz results found. Please complete a quiz first.")
                    return
                
                # Create quiz answers window
                quiz_window = tk.Toplevel(parent_window)
                quiz_window.title("Quiz Answers")
                quiz_window.geometry("700x700")

                tk.Label(quiz_window, text="Quiz Answers", font=("Helvetica", 14, "bold")).pack(pady=10)
                text_display = ScrolledText(quiz_window, wrap="word", font=("Helvetica", 11),
                                            width=80, height=25)
                text_display.pack(padx=10, pady=10, fill="both", expand=True)

                # Read and display quiz results
                with open(data_path, newline="") as file:
                    csv_reader = csv.DictReader(file)
                    for index, row in enumerate(csv_reader, 1):
                        question_text = row["Question"]
                        user_answer = row["Your Answer"]
                        correct_answer = row["Correct Answer"]
                        correctness_flag = row["Correct?"]
                        is_correct = str(correctness_flag) == "1"
                        result_label = "Correct" if is_correct else "Incorrect"
                        color_style = "green_text" if is_correct else "red_text"
                        # Display formatted results
                        text_display.insert("end", f"Q{index}. {question_text}\n", "bold")
                        text_display.insert("end", f"Your answer: {user_answer}\n")
                        text_display.insert("end", f"Correct answer: {correct_answer}\n")
                        # Display result with color coding
                        text_display.insert("end", f"Result: {result_label}\n\n", color_style)
                
                # Instructions for graph generation
                text_display.insert("end", "Plots can be generated and saved using the button below.\n")
                text_display.tag_configure("bold", font=("Helvetica", 11, "bold"))
                text_display.tag_configure("green_text", foreground="green")
                text_display.tag_configure("red_text", foreground="red")
                text_display.config(state="disabled")

                # Button frame
                button_frame = tk.Frame(quiz_window, bg=quiz_window.cget("bg"))
                button_frame.pack(pady=10, fill="x")

                # Graph generation
                def generate_quiz_graphs():
                    plot_path = analyze_quiz()
                    messagebox.showinfo("Graph Generated", f"Quiz plot saved to:\n{plot_path}")

                # Close button
                tk.Button(
                    quiz_window,
                    text="Close",
                    command=quiz_window.destroy,
                    bg=Config.PRIMARY_COLOR,
                    fg="white",
                    relief="flat",
                    font=("Helvetica", 11, "bold"),
                    width=15
                ).pack(pady=(5, 2))

                # Generate Graphs button
                tk.Button(
                    quiz_window,
                    text="Generate Graphs",
                    command=generate_quiz_graphs,
                    bg="#6c757d",
                    fg="white",
                    relief="flat",
                    font=("Helvetica", 11, "bold"),
                    width=15
                ).pack(pady=(2, 10))

            # Fitts' Law summary window
            def show_fitts_summary(parent_window):
                data_directory = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
                
                # Gather available Fitts' Law CSV files
                ordered_modes = ["normal", "mild", "moderate", "severe"]
                csv_files = [f"fitts_{m}.csv" for m in ordered_modes if os.path.exists(os.path.join(data_directory, f"fitts_{m}.csv"))]

                # If no files found, show message
                if not csv_files:
                    messagebox.showinfo("No Results", "No Fitts' Law CSV files found.")
                    return

                # Create Fitts' Law results window
                fitts_window = tk.Toplevel(parent_window)
                fitts_window.title("Fitts' Law Results")
                fitts_window.geometry("700x700")

                tk.Label(fitts_window, text="Fitts' Law Results (ordered by severity)",
                         font=("Helvetica", 14, "bold")).pack(pady=10)

                # Create a scrollable text area
                text_display = ScrolledText(fitts_window, wrap="word", font=("Helvetica", 11),
                                            width=80, height=25)
                text_display.pack(padx=10, pady=10, fill="both", expand=True)

                # Read and display summary statistics for each CSV file
                for file_name in csv_files:
                    file_path = os.path.join(data_directory, file_name)
                    try:
                        df = pd.read_csv(file_path)
                        num_trials = len(df)
                        average_time_ms = df["Time (ms)"].mean() if "Time (ms)" in df else float("nan")
                        text_display.insert("end", f"{file_name}\n", "bold")
                        text_display.insert("end", f"  Trials: {num_trials}\n")
                        text_display.insert("end", f"  Avg Movement Time: {average_time_ms:.2f} ms\n\n")
                    except Exception as e:
                        text_display.insert("end", f"{file_name}\n", "bold")
                        text_display.insert("end", f"  Error reading file: {e}\n\n")
                
                # Instructions for graph generation
                text_display.insert("end", "Plots can be generated and saved using the button below.\n")
                text_display.tag_configure("bold", font=("Helvetica", 11, "bold"))
                text_display.config(state="disabled")

                # Button frame
                button_frame = tk.Frame(fitts_window, bg=Config.BG_COLOR)
                button_frame.pack(pady=10)

                # Graph generation
                def generate_fitts_graphs():
                    generated_plots = []
                    # Generate plots for each CSV file
                    for file_name in csv_files:
                        plot_path = analyze_fitts(file_name)
                        if plot_path:
                            generated_plots.append(plot_path)
                    message_text = "\n".join(generated_plots) if generated_plots else "No files processed."
                    messagebox.showinfo("Graphs Generated", f"Plots saved to:\n{message_text}")

                # Close button
                tk.Button(
                    fitts_window,
                    text="Close",
                    command=fitts_window.destroy,
                    bg=Config.PRIMARY_COLOR,
                    fg="white",
                    relief="flat",
                    font=("Helvetica", 11, "bold"),
                    width=15
                ).pack(pady=(5, 2))

                # Generate Graphs button
                tk.Button(
                    fitts_window,
                    text="Generate Graphs",
                    command=generate_fitts_graphs,
                    bg="#6c757d",
                    fg="white",
                    relief="flat",
                    font=("Helvetica", 11, "bold"),
                    width=15
                ).pack(pady=(2, 10))

            # Menu handler
            def run_analysis(selected_option):
                # Close menu and run selected analysis
                analysis_menu.destroy()
                if selected_option == "quiz":
                    show_quiz_answers_from_file(main_window)
                elif selected_option == "fitts":
                    show_fitts_summary(main_window)
                else:
                    show_quiz_answers_from_file(main_window)
                    show_fitts_summary(main_window)

            # Create buttons for each analysis option
            for label, option_key in analysis_options:
                tk.Button(analysis_menu, text=label, width=25, height=2,
                          command=lambda key=option_key: run_analysis(key),
                          bg="white", relief="flat", font=("Helvetica", 11)).pack(pady=5)

        # Analyze Results Button
        tk.Button(main_window, text="Analyze Results", width=25, height=2,
                  command=open_analysis_menu,
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

    # Run the main loop
    main_window.mainloop()


if __name__ == "__main__":
    main()
