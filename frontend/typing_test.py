import tkinter as tk
import random, time, json, os, difflib
from tkinter import messagebox
from frontend.api_client import upload_test
from app.config import Config
from frontend.learn_popup import show_learn_popup

# runs the test and sets the default impairment level to be normal
def run_typing_test(parent_window, user_id, impairment_level="normal"):

    # create window for the test
    typing_window = tk.Toplevel(parent_window)
    typing_window.title(f"Typing Test ({impairment_level.capitalize()})")
    typing_window.configure(bg=Config.BG_COLOR)

    # Load QWERTY neighbor map
    neighbor_file_path = os.path.join(os.path.dirname(__file__), "../assets/qwerty_neighbors.json")
    with open(neighbor_file_path, "r") as file:
        qwerty_neighbors = json.load(file)

    # Word pool for user to type
    word_pool = [
        "coord", "reflex", "motor", "balance", "focus", "attention",
        "hand", "foot", "eye", "leg", "arm", "brain", "speed", "control",
        "vision", "memory", "timing", "reaction", "alert", "motion",
        "judgment", "steady", "signal", "move", "respond", "target"
    ]

    # picks random words from the word pool
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

    # entry form for the user to type in
    typing_entry = tk.Entry(typing_window, font=("Arial", 14), width=50, relief="flat", highlightthickness=2)
    typing_entry.pack(pady=15)
    typing_entry.focus_set()

    # error simulation probabilities based on impairment level
    error_probabilities = {"normal": 0.0, "mild": 0.10, "moderate": 0.20, "severe": 0.40}

    # simulated error chance based on impairment level
    simulated_error_chance = error_probabilities.get(impairment_level, 0.0)

    test_start_time = None

    # start timer once user starts typing
    def start_timer(event):
        nonlocal test_start_time
        if test_start_time is None and len(event.char) == 1:
            test_start_time = time.time()

    # binds the first key pressed to start the timer
    typing_entry.bind("<KeyPress>", start_timer, add="+")

    # adds a random typo based on the QWERTY layout
    def maybe_inject_typo(event):

        # only considers printable characters
        if len(event.char) != 1 or not event.char.isalpha():
            return
        if random.random() >= simulated_error_chance:
            return

        # gets nearby characters from QWERTY layout
        current_char = event.char.lower()
        nearby_chars = qwerty_neighbors.get(current_char, [])
        if not nearby_chars:
            return

        # chooses a random nearby character to substitute
        replacement_char = random.choice(nearby_chars)

        # adds the substitution after the key is pressed
        def apply_typo_substitution():
            try:

                # gets the current cursor position
                cursor_position = typing_entry.index(tk.INSERT)
                if cursor_position <= 0:
                    return
                
                # replaces the last typed character with a substitution
                typing_entry.delete(cursor_position - 1)
                typing_entry.insert(cursor_position - 1, replacement_char)

                # makes sure the cursor is back at the end position
                typing_entry.icursor(cursor_position)
            except tk.TclError:
                pass

        # schedules the substitution to occur after the key event
        typing_window.after_idle(apply_typo_substitution)

    # bind to inect a typo based on error chance
    typing_entry.bind("<KeyPress>", maybe_inject_typo, add="+")

    # finishes and evaluates the test
    def finish_typing_test():
        if test_start_time is None:
            messagebox.showinfo("Typing Test", "Please type something first.")
            return

        # calculates time elapsed and accuracy
        total_time_elapsed = time.time() - test_start_time
        user_typed_text = typing_entry.get().strip()

        # calculates hybrid (sequence-matching) accuracy
        sequence_matcher = difflib.SequenceMatcher(None, target_text.strip(), user_typed_text)
        typing_accuracy = sequence_matcher.ratio() * 100

        # uploads the results
        upload_test(user_id, total_time_elapsed, typing_accuracy, impairment_level)
        messagebox.showinfo(
            "Typing Test Results",
            f"Accuracy: {typing_accuracy:.1f}%\nTime: {total_time_elapsed:.1f}s"
        )
        show_learn_popup(parent_window, "typing")
        typing_window.destroy()

    # submit button for when the user is finished typing
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

    # binds the ENTER key to also finish the test
    typing_window.bind("<Return>", lambda event: finish_typing_test())

    # provides instrusctions on how to do the test
    messagebox.showinfo("How to Play", "Type the words that appear on the screen as quickly as possible")
    typing_window.lift()
    typing_window.focus_force()
    typing_entry.focus_set()
