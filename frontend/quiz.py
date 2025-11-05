import csv
import os
import tkinter as tk
import json
from frontend.api_client import upload_quiz
from app.models import QuizQuestion, Quiz

# ensure a /data directory exists
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

    question_label = tk.Label(win, text="", wraplength=400)
    question_label.pack(pady=10)
    var = tk.IntVar()

    buttons = [tk.Radiobutton(win, variable=var, value=i) for i in range(3)]
    for b in buttons:
        b.pack(anchor="w")

    next_button = tk.Button(win, text="Next")
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
        tk.Label(win, text=f"Score: {score}/{questions.num_questions}").pack()
        tk.Label(win, text=f"Results saved to {csv_name}", fg="gray").pack()
        tk.Button(win, text="Finish", command=win.destroy).pack(pady=10)

    def next_q():
        nonlocal score
        q = questions.current_question()
        chosen = var.get()
        correct = q.answer
        results.append([q.prompt, q.choices[chosen], q.choices[correct], int(q.is_correct(chosen))])
        if q.is_correct(chosen):
            score += 1

        questions.next_question()
        if questions.current_question_index >= questions.num_questions:
            finish()
        else:
            show_current()

    next_button.config(command=next_q)
    show_current()

