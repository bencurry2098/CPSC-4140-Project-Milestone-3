import tkinter as tk
import random, time, json, os, difflib
from tkinter import messagebox
from frontend.api_client import upload_test
from app.config import Config


def run_typing_test(root, user_id, mode="normal"):
    win = tk.Toplevel(root)
    win.title(f"Typing Test ({mode.capitalize()})")
    win.configure(bg=Config.BG_COLOR)

    # --- Load QWERTY neighbor map ---
    neighbor_file = os.path.join(os.path.dirname(__file__), "../assets/qwerty_neighbors.json")
    with open(neighbor_file, "r") as f:
        neighbors = json.load(f)

    # --- Word pool ---
    words = [
        "coord", "reflex", "motor", "balance", "focus", "attention",
        "hand", "foot", "eye", "leg", "arm", "brain", "speed", "control",
        "vision", "memory", "timing", "reaction", "alert", "motion",
        "judgment", "steady", "signal", "move", "respond", "target"
    ]

    # --- Target text ---
    text = " ".join(random.choices(words, k=6))
    tk.Label(
        win,
        text=text,
        font=("Arial", 14),
        bg=Config.BG_COLOR,
        fg="black",
        wraplength=700,
        justify="center"
    ).pack(pady=20)

    # --- Entry box ---
    entry = tk.Entry(win, font=("Arial", 14), width=50, relief="flat", highlightthickness=2)
    entry.pack(pady=15)
    entry.focus_set()

    # --- Error simulation probabilities ---
    error_chances = {"normal": 0.0, "mild": 0.10, "moderate": 0.20, "severe": 0.40}
    error_chance = error_chances.get(mode, 0.0)

    start_time = None

    # Start timer on first printable key
    def start_timer(event):
        nonlocal start_time
        if start_time is None and len(event.char) == 1:
            start_time = time.time()

    entry.bind("<KeyPress>", start_timer, add="+")

    # Inject substitution based on keyboard proximity
    def maybe_inject(event):
        if len(event.char) != 1 or not event.char.isalpha():
            return
        if random.random() >= error_chance:
            return

        char = event.char.lower()
        nearby = neighbors.get(char, [])
        if not nearby:
            return

        substitute = random.choice(nearby)

        def do_substitute():
            try:
                pos = entry.index(tk.INSERT)
                if pos <= 0:
                    return
                entry.delete(pos - 1)
                entry.insert(pos - 1, substitute)
                entry.icursor(pos)
            except tk.TclError:
                pass

        win.after_idle(do_substitute)

    entry.bind("<KeyPress>", maybe_inject, add="+")

    # --- Finish and evaluate test ---
    def finish():
        if start_time is None:
            messagebox.showinfo("Typing Test", "Please type something first.")
            return

        elapsed = time.time() - start_time
        typed = entry.get().strip()

        # --- Hybrid (sequence-matching) accuracy ---
        matcher = difflib.SequenceMatcher(None, text.strip(), typed)
        accuracy = matcher.ratio() * 100

        upload_test(user_id, elapsed, accuracy, mode)
        messagebox.showinfo(
            "Typing Test Results",
            f"Accuracy: {accuracy:.1f}%\nTime: {elapsed:.1f}s"
        )

        from frontend.learn_popup import show_learn_popup
        show_learn_popup(win, "typing")
        win.destroy()

    # --- Submit button ---
    tk.Button(
        win,
        text="Submit",
        command=finish,
        bg=Config.PRIMARY_COLOR,
        fg="white",
        font=("Helvetica", 11, "bold"),
        relief="flat",
        width=12
    ).pack(pady=20)

    win.bind("<Return>", lambda event: finish())
    messagebox.showinfo("How to Play", "Type the words that appear on the screen as quickly as possible")
    win.lift()
    win.focus_force()
    entry.focus_set()
