import tkinter as tk
import csv, os
from frontend.api_client import upload_quiz

# ensure a /data directory exists
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)

QUESTIONS = [
    ("At what BAC do most people start to show slowed reaction time?", ["0.02", "0.05", "0.08"], 0),
    ("Which organ primarily metabolizes alcohol?", ["Liver", "Kidneys", "Pancreas"], 0),
    ("What is the legal BAC limit for driving in most US states?", ["0.04", "0.08", "0.10"], 1),
    ("Alcohol affects which of the following first?", ["Motor skills", "Judgment", "Balance"], 1),
]

def run_quiz(root, user_id):
    win = tk.Toplevel(root)
    win.title("Alcohol Knowledge Quiz")
    score, q_index = 0, 0
    results = []

    question_label = tk.Label(win, text="", wraplength=400)
    question_label.pack(pady=10)
    var = tk.IntVar()

    def next_q():
        nonlocal q_index, score
        if q_index > 0:
            correct = QUESTIONS[q_index-1][2]
            chosen = var.get()
            results.append([QUESTIONS[q_index-1][0], QUESTIONS[q_index-1][1][chosen], 
                            QUESTIONS[q_index-1][1][correct], int(chosen == correct)])
            if chosen == correct:
                score += 1
        if q_index < len(QUESTIONS):
            question_label.config(text=QUESTIONS[q_index][0])
            for i, b in enumerate(buttons):
                b.config(text=QUESTIONS[q_index][1][i])
            var.set(-1)
            q_index += 1
        else:
            upload_quiz(user_id, score, len(QUESTIONS))
            # save results to CSV
            csv_name = os.path.join(DATA_DIR, "quiz_results.csv")
            with open(csv_name, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Question", "Your Answer", "Correct Answer", "Correct?"])
                writer.writerows(results)
            tk.Label(win, text=f"Score: {score}/{len(QUESTIONS)}").pack()
            tk.Label(win, text=f"Results saved to {csv_name}", fg="gray").pack()

    buttons = [tk.Radiobutton(win, variable=var, value=i) for i in range(3)]
    for b in buttons: b.pack(anchor="w")
    tk.Button(win, text="Next", command=next_q).pack(pady=10)
    next_q()
