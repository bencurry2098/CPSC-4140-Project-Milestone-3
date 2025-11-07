import tkinter as tk
import random, time, json, os, difflib
from tkinter import messagebox
from frontend.api_client import upload_test
from app.config import Config
from frontend.learn_popup import show_learn_popup
from frontend.learn_popup import show_learn_popup

# Run the typing test GUI
def run_typing_test(parent_window, user_id, impairment_level="normal"):
    # Create typing test window
    typing_window = tk.Toplevel(parent_window)
    typing_window.title(f"Typing Test ({impairment_level.capitalize()})")
    typing_window.configure(bg=Config.BG_COLOR)

    # Load QWERTY neighbor map
    neighbor_file_path = os.path.join(os.path.dirname(__file__), "../assets/qwerty_neighbors.json")
    with open(neighbor_file_path, "r") as file:
        qwerty_neighbors = json.load(file)

    # Word pool
    word_pool = [
        "coord", "reflex", "motor", "balance", "focus", "attention",
        "hand", "foot", "eye", "leg", "arm", "brain", "speed", "control",
        "vision", "memory", "timing", "reaction", "alert", "motion",
        "judgment", "steady", "signal", "move", "respond", "target"
    ]

    # Target text
    target_text = " ".join(random.choices(word_pool, k=6))
    tk.Label(
        typing_window,
        text=target_text,
        font=("Arial", 14),
        bg=Config.BG_COLOR,
        fg="black",
        wraplength=700,
        justify="center"
    ).pack(pady=20)

    # Entry box
    typing_entry = tk.Entry(typing_window, font=("Arial", 14), width=50, relief="flat", highlightthickness=2)
    typing_entry.pack(pady=15)
    typing_entry.focus_set()

    # Error simulation probabilities
    error_probabilities = {"normal": 0.0, "mild": 0.10, "moderate": 0.20, "severe": 0.40}
    # Simulated error chance based on impairment level
    simulated_error_chance = error_probabilities.get(impairment_level, 0.0)

    test_start_time = None

    # Start timer on first printable key
    def start_timer(event):
        nonlocal test_start_time
        if test_start_time is None and len(event.char) == 1:
            test_start_time = time.time()

    # Bind to start timer, use add to not override other bindings
    typing_entry.bind("<KeyPress>", start_timer, add="+")

    # Inject substitution based on keyboard proximity
    def maybe_inject_typo(event):
        # Only consider printable characters
        if len(event.char) != 1 or not event.char.isalpha():
            return
        if random.random() >= simulated_error_chance:
            return

        # Get nearby characters from QWERTY layout
        current_char = event.char.lower()
        nearby_chars = qwerty_neighbors.get(current_char, [])
        if not nearby_chars:
            return

        # Choose a random nearby character to substitute
        replacement_char = random.choice(nearby_chars)

        # Function to apply the substitution after the key event
        def apply_typo_substitution():
            try:
                # Get the current cursor position
                cursor_position = typing_entry.index(tk.INSERT)
                if cursor_position <= 0:
                    return
                # Replace the last typed character with the replacement character
                typing_entry.delete(cursor_position - 1)
                typing_entry.insert(cursor_position - 1, replacement_char)
                # Restore cursor position
                typing_entry.icursor(cursor_position)
            except tk.TclError:
                pass
        # Schedule the substitution to occur after the key event
        typing_window.after_idle(apply_typo_substitution)

    # Bind to maybe inject typo, use add to not override other bindings
    typing_entry.bind("<KeyPress>", maybe_inject_typo, add="+")

    # Finish and evaluate test
    def finish_typing_test():
        if test_start_time is None:
            messagebox.showinfo("Typing Test", "Please type something first.")
            return

        # Calculate time elapsed and accuracy
        total_time_elapsed = time.time() - test_start_time
        user_typed_text = typing_entry.get().strip()

        # Calculate hybrid (sequence-matching) accuracy
        sequence_matcher = difflib.SequenceMatcher(None, target_text.strip(), user_typed_text)
        typing_accuracy = sequence_matcher.ratio() * 100

        # Upload results
        upload_test(user_id, total_time_elapsed, typing_accuracy, impairment_level)
        messagebox.showinfo(
            "Typing Test Results",
            f"Accuracy: {typing_accuracy:.1f}%\nTime: {total_time_elapsed:.1f}s"
        )

        show_learn_popup(typing_window, "typing")
        typing_window.destroy()

    # Submit button
    tk.Button(
        typing_window,
        text="Submit",
        command=finish_typing_test,
        bg=Config.PRIMARY_COLOR,
        fg="white",
        font=("Helvetica", 11, "bold"),
        relief="flat",
        width=12
    ).pack(pady=20)

    typing_window.bind("<Return>", lambda event: finish_typing_test())
    messagebox.showinfo("How to Play", "Type the words that appear on the screen as quickly as possible")
    typing_window.lift()
    typing_window.focus_force()
    typing_entry.focus_set()
