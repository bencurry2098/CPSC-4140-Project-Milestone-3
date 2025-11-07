import csv
import os
import tkinter as tk
import json
from tkinter.scrolledtext import ScrolledText
from frontend.api_client import upload_quiz
from app.models import QuizQuestion, Quiz

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)

QUESTION_JSON_PATH = os.path.join(os.getcwd(), 'assets', 'quiz_question_data.json')


def run_quiz(root, user_id):
    with open(QUESTION_JSON_PATH, 'r') as f:
        question_data = json.load(f)
        questions = Quiz([QuizQuestion(q['prompt'], q['choices'], q['answer']) for q in question_data])

    win = tk.Toplevel(root)
    win.title("Alcohol Knowledge Quiz")
    score = 0
    results = []

    question_label = tk.Label(win, text="", wraplength=400, font=("Helvetica", 12))
    question_label.pack(pady=10)
    var = tk.IntVar()

    buttons = [tk.Radiobutton(win, variable=var, value=i, font=("Helvetica", 11)) for i in range(3)]
    for b in buttons:
        b.pack(anchor="w")

    next_button = tk.Button(win, text="Next", font=("Helvetica", 11))
    next_button.pack(pady=10)

    def show_current():
        q = questions.current_question()
        question_label.config(text=q.prompt)
        for i, b in enumerate(buttons):
            b.config(text=q.choices[i])
        var.set(-1)

    def finish():
        next_button.pack_forget()
        upload_quiz(user_id, score, questions.num_questions)
        csv_name = os.path.join(DATA_DIR, "quiz_results.csv")
        with open(csv_name, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Question", "Your Answer", "Correct Answer", "Correct?"])
            writer.writerows(results)

        tk.Label(win, text=f"Score: {score}/{questions.num_questions}",
                 font=("Helvetica", 12, "bold")).pack(pady=(10, 0))
        tk.Label(win, text=f"Results saved to {csv_name}",
                 fg="gray", font=("Helvetica", 10)).pack()

        # Buttons
        tk.Button(win, text="Show Answers", command=lambda: show_answers_window(results),
                  bg="#0d6efd", fg="white", relief="flat", font=("Helvetica", 11, "bold"),
                  width=15).pack(pady=10)

        tk.Button(win, text="Retake Quiz", command=lambda: [win.destroy(), run_quiz(root, user_id)],
                  bg="#6c757d", fg="white", relief="flat", font=("Helvetica", 11), width=15).pack(pady=5)

        tk.Button(win, text="Finish", command=win.destroy,
                  bg="#198754", fg="white", relief="flat", font=("Helvetica", 11), width=15).pack(pady=10)

    def next_q():
        nonlocal score
        q = questions.current_question()
        chosen = var.get()
        if chosen == -1:
            return  # do nothing if no choice selected
        correct = q.answer
        results.append([q.prompt, q.choices[chosen], q.choices[correct], int(q.is_correct(chosen))])
        if q.is_correct(chosen):
            score += 1

        questions.next_question()
        if questions.current_question_index >= questions.num_questions:
            finish()
        else:
            show_current()

    def show_answers_window(results):
        answers_win = tk.Toplevel(win)
        answers_win.title("Quiz Answers")
        answers_win.geometry("700x500")

        tk.Label(answers_win, text="Quiz Answers",
                 font=("Helvetica", 14, "bold")).pack(pady=10)

        text_box = ScrolledText(answers_win, wrap="word", font=("Helvetica", 11), width=80, height=25)
        text_box.pack(padx=10, pady=10, fill="both", expand=True)

        for i, row in enumerate(results, 1):
            q_text, your_ans, correct_ans, correct_flag = row
            status = "Correct" if correct_flag else "Incorrect"
            text_box.insert("end", f"Q{i}. {q_text}\n", "bold")
            text_box.insert("end", f"Your answer: {your_ans}\n")
            text_box.insert("end", f"Correct answer: {correct_ans}\n")
            text_box.insert("end", f"Result: {status}\n\n")

        text_box.tag_configure("bold", font=("Helvetica", 11, "bold"))
        text_box.config(state="disabled")

        tk.Button(answers_win, text="Close", command=answers_win.destroy,
                  bg="#0d6efd", fg="white", relief="flat", font=("Helvetica", 11, "bold"),
                  width=15).pack(pady=10)

    next_button.config(command=next_q)
    show_current()
