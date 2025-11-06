import tkinter as tk
from tkinter import messagebox
import random, time
from app.config import Config

def run_typing_test(root, user_id, mode="normal"):
    # --- Create window but keep it hidden initially ---
    win = tk.Toplevel(root)
    win.withdraw()  # prevent flicker
    win.title(f"Typing Test ({mode.capitalize()})")

    # Center window relative to parent
    root.update_idletasks()
    parent_x, parent_y = root.winfo_x(), root.winfo_y()
    parent_w, parent_h = root.winfo_width(), root.winfo_height()
    width, height = 600, 250
    x = parent_x + (parent_w // 2) - (width // 2)
    y = parent_y + (parent_h // 2) - (height // 2)
    win.geometry(f"{width}x{height}+{x}+{y}")
    win.transient(root)

    # --- Now show it after layout is ready ---
    win.deiconify()

    # --- Word pool ---
    words = [
        "coord", "reflex", "motor", "balance", "focus", "attention",
        "hand", "foot", "eye", "leg", "arm", "brain",
        "drive", "safe", "alert", "react", "speed", "drink",
        "crash", "risk", "limit", "judge", "blur", "delay"
    ]

    text = " ".join(random.choices(words, k=6))
    tk.Label(win, text=text, font=("Arial", 14)).pack(pady=10)

    entry = tk.Entry(win, font=("Arial", 14), width=50)
    entry.pack(pady=10)
    entry.focus_set()

    start = time.time()

    error_chances = {"normal": 0.0, "mild": 0.1, "moderate": 0.2, "severe": 0.4}
    error_chance = error_chances.get(mode, 0.0)

    def make_button_accessible(button):
        button.bind("<Return>", lambda event: button.invoke())
        button.configure(takefocus=True)

    qwerty_neighbors = {
        "q": "was", "w": "qesd", "e": "wsdr", "r": "edft", "t": "rfgy",
        "y": "tghu", "u": "yhji", "i": "ujko", "o": "iklp", "p": "ol",
        "a": "qwsz", "s": "awedxz", "d": "serfcx", "f": "drtgcv", "g": "ftyhbv",
        "h": "gyujnb", "j": "huikmn", "k": "jiolm,", "l": "kop;", "z": "asx",
        "x": "zsdc", "c": "xdfv", "v": "cfgb", "b": "vghn", "n": "bhjm", "m": "njk"
    }

    def on_key(event):
        if event.char.isalpha() and random.random() < error_chance:
            letter = event.char.lower()
            if letter in qwerty_neighbors:
                replacement = random.choice(qwerty_neighbors[letter])
                entry.insert(tk.END, replacement)
            else:
                entry.insert(tk.END, random.choice("abcdefghijklmnopqrstuvwxyz"))
            return "break"

    entry.bind("<Key>", on_key)

    def finish():
        elapsed = time.time() - start
        typed = entry.get()
        correct_chars = sum(a == b for a, b in zip(text, typed))
        total_chars = max(len(text), len(typed))
        accuracy = (correct_chars / total_chars) * 100 if total_chars > 0 else 0
        messagebox.showinfo("Result", f"Accuracy: {accuracy:.1f}%\nTime: {elapsed:.1f}s")
        win.destroy()

    submit_btn = tk.Button(win, text="Submit", command=finish, font=("Arial", 12))
    submit_btn.pack(pady=10)
    make_button_accessible(submit_btn)

    entry.bind("<Return>", lambda event: finish())
    win.bind("<Escape>", lambda event: win.destroy())
