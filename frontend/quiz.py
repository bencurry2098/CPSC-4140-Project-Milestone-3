import csv
import os
import tkinter as tk
import json
from tkinter.scrolledtext import ScrolledText
from frontend.api_client import upload_quiz
from app.models import QuizQuestion, Quiz

# Create data directory if it doesn't exist
DATA_DIRECTORY = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(DATA_DIRECTORY, exist_ok=True)

# Path to quiz questions JSON file
QUESTION_FILE_PATH = os.path.join(os.getcwd(), 'assets', 'quiz_question_data.json')

# Run the quiz GUI
def run_quiz(parent_window, user_id):
    # Load questions
    with open(QUESTION_FILE_PATH, 'r') as file:
        question_data = json.load(file)
        quiz_object = Quiz([QuizQuestion(q['prompt'], q['choices'], q['answer']) for q in question_data])

    # Create quiz window
    quiz_window = tk.Toplevel(parent_window)
    quiz_window.title("Alcohol Knowledge Quiz")
    total_score = 0
    answer_records = []

    # GUI elements
    question_label = tk.Label(quiz_window, text="", wraplength=400, font=("Helvetica", 12))
    question_label.pack(pady=10)
    selected_choice = tk.IntVar()

    # Answer radio buttons
    answer_buttons = [tk.Radiobutton(quiz_window, variable=selected_choice, value=i, font=("Helvetica", 11)) for i in range(3)]
    for button in answer_buttons:
        button.pack(anchor="w")

    # Next button
    next_button = tk.Button(quiz_window, text="Next", font=("Helvetica", 11))
    next_button.pack(pady=10)

    # Display the current question
    def display_current_question():
        current_question = quiz_object.current_question()
        question_label.config(text=current_question.prompt)
        # Update answer choices
        for i, button in enumerate(answer_buttons):
            button.config(text=current_question.choices[i])
        # Reset selected choice
        selected_choice.set(-1)

    # Finish the quiz and save results
    def finish_quiz():
        # Unmap question elements
        question_label.pack_forget()
        next_button.pack_forget()
        # Unmap answer buttons
        for button in answer_buttons:
            button.pack_forget()
            
        # Upload results to backend
        upload_quiz(user_id, total_score, quiz_object.num_questions)
        results_path = os.path.join(DATA_DIRECTORY, "quiz_results.csv")

        # Save results to CSV
        with open(results_path, "w", newline="") as csv_file:
            writer = csv.writer(csv_file)
            # Write header then data
            writer.writerow(["Question", "Your Answer", "Correct Answer", "Correct?"])
            writer.writerows(answer_records)

        # Display final score and results path
        tk.Label(quiz_window, text=f"Score: {total_score}/{quiz_object.num_questions}",
                 font=("Helvetica", 12, "bold")).pack(pady=(10, 0))
        tk.Label(quiz_window, text=f"Results saved to {results_path}",
                 fg="gray", font=("Helvetica", 10)).pack()

        # Show answers button
        tk.Button(quiz_window, text="Show Answers", command=lambda: show_answers_window(answer_records),
                  bg="#0d6efd", fg="white", relief="flat", font=("Helvetica", 11, "bold"),
                  width=15).pack(pady=10)

        # Retake quiz button
        tk.Button(quiz_window, text="Retake Quiz", command=lambda: [quiz_window.destroy(), run_quiz(parent_window, user_id)],
                  bg="#6c757d", fg="white", relief="flat", font=("Helvetica", 11), width=15).pack(pady=5)

        # Finish button
        tk.Button(quiz_window, text="Finish", command=quiz_window.destroy,
                  bg="#198754", fg="white", relief="flat", font=("Helvetica", 11), width=15).pack(pady=10)


    # Handle next question
    def handle_next_question():
        nonlocal total_score
        current_question = quiz_object.current_question()
        selected_index = selected_choice.get()
        # Do nothing if no choice selected
        if selected_index == -1:
            return 

        # Record answer
        correct_index = current_question.answer
        # Append question, user answer, correct answer, correctness flag
        answer_records.append([current_question.prompt,
                               current_question.choices[selected_index],
                               current_question.choices[correct_index],
                               int(current_question.is_correct(selected_index))])
        if current_question.is_correct(selected_index):
            # Increment score
            total_score += 1

        # Move to next question or finish  
        quiz_object.next_question()
        if quiz_object.current_question_index >= quiz_object.num_questions:
            finish_quiz()
        else:
            display_current_question()

    # Show answers window
    def show_answers_window(results):
        answers_window = tk.Toplevel(quiz_window)
        answers_window.title("Quiz Answers")
        answers_window.geometry("700x500")

        tk.Label(answers_window, text="Quiz Answers", font=("Helvetica", 14, "bold")).pack(pady=10)

        # Scrollable text area for answers
        text_area = ScrolledText(answers_window, wrap="word", font=("Helvetica", 11), width=80, height=25)
        text_area.pack(padx=10, pady=10, fill="both", expand=True)
        
        # Tag configurations for color coding
        text_area.tag_configure("bold", font=("Helvetica", 11, "bold"))
        text_area.tag_configure("correct", foreground="green")
        text_area.tag_configure("incorrect", foreground="red")

        # Insert each question and answer into the text area
        for i, record in enumerate(results, 1):
            question_text, user_answer, correct_answer, correctness_flag = record
            answer_status = "Correct" if correctness_flag else "Incorrect"
            text_area.insert("end", f"Q{i}. {question_text}\n", "bold")
            text_area.insert("end", f"Your answer: {user_answer}\n")
            text_area.insert("end", f"Correct answer: {correct_answer}\n")
            if correctness_flag:
                text_area.insert("end", f"Result: {answer_status}\n\n", "correct")
            else:
                text_area.insert("end", f"Result: {answer_status}\n\n", "incorrect")

        text_area.config(state="disabled")

        # Close button
        tk.Button(answers_window, text="Close", command=answers_window.destroy,
                  bg="#0d6efd", fg="white", relief="flat", font=("Helvetica", 11, "bold"),
                  width=15).pack(pady=10)

    # Set next button command and display first question
    next_button.config(command=handle_next_question)
    display_current_question()
