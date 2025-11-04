import tkinter as tk
from tkinter import messagebox
import random, math, time, csv, os
from frontend.api_client import upload_test
from app.config import Config
from PIL import Image, ImageTk, ImageDraw

def run_typing_test(root, user_id, mode="normal"):
    win = tk.Toplevel(root)
    win.title(f"Typing Test ({mode.capitalize()})")

    words = ["coordination", "reflex", "motor", "balance", "focus", "attention"]
    text = " ".join(random.choices(words, k=8))
    tk.Label(win, text=text, font=("Arial", 14)).pack(pady=10)
    entry = tk.Entry(win, font=("Arial", 14), width=50)
    entry.pack(pady=10)
    start = time.time()

    levels = {
        "normal": {"delay": 0, "error_chance": 0},
        "mild": {"delay": 50, "error_chance": 0.05},
        "moderate": {"delay": 100, "error_chance": 0.1},
        "severe": {"delay": 200, "error_chance": 0.2},
    }
    delay, error_chance = levels.get(mode, levels["normal"]).values()

    def on_key(event):
        if delay:
            win.after(delay)
        if random.random() < error_chance:
            entry.insert(tk.END, random.choice("abcdefghijklmnopqrstuvwxyz"))
            return "break"

    def finish():
        elapsed = time.time() - start
        typed = entry.get().strip()
        accuracy = sum(a == b for a, b in zip(text, typed)) / len(text) * 100
        messagebox.showinfo("Result", f"Accuracy: {accuracy:.1f}%\nTime: {elapsed:.1f}s")
        win.destroy()

    entry.bind("<Key>", on_key)
    tk.Button(win, text="Submit", command=finish).pack(pady=10)
