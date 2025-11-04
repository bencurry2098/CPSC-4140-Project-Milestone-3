import tkinter as tk
from tkinter import messagebox
import random, time

def run_typing_test(root, user_id, mode="normal"):
    win = tk.Toplevel(root)
    win.title(f"Typing Test ({mode.capitalize()})")

    # Word pool: all words 8 letters or less
    words = ["coord", "reflex", "motor", "balance", "focus", "attention", 
             "hand", "foot", "eye", "leg", "arm", "brain"]

    # Pick 6 words at random for the test
    text = " ".join(random.choices(words, k=6))
    tk.Label(win, text=text, font=("Arial", 14)).pack(pady=10)

    entry = tk.Entry(win, font=("Arial", 14), width=50)
    entry.pack(pady=10)
    entry.focus_set()
    start = time.time()

    # Set replacement chance based on severity
    error_chances = {
        "normal": 0.0,
        "mild": 0.1,       # small chance
        "moderate": 0.2,   # medium chance
        "severe": 0.4      # high chance
    }
    error_chance = error_chances.get(mode, 0.0)

    def on_key(event):
        # Only replace normal letters (ignore space, backspace, etc.)
        if event.char.isalpha() and random.random() < error_chance:
            entry.insert(tk.END, random.choice("abcdefghijklmnopqrstuvwxyz"))
            return "break"  # prevent the original key from registering

    def finish():
        elapsed = time.time() - start
        typed = entry.get()
        correct_chars = sum(a == b for a, b in zip(text, typed))
        total_chars = max(len(text), len(typed))
        accuracy = (correct_chars / total_chars) * 100
        messagebox.showinfo("Result", f"Accuracy: {accuracy:.1f}%\nTime: {elapsed:.1f}s")
        win.destroy()

    entry.bind("<Key>", on_key)
    tk.Button(win, text="Submit", command=finish).pack(pady=10)
