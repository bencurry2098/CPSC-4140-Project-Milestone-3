import tkinter as tk
from tkinter import messagebox
import random, math
from frontend.api_client import upload_test
from app.config import Config

def run_balance_game(root, user_id, mode="normal"):
    win = tk.Toplevel(root)
    win.title(f"Balance Game ({mode.capitalize()})")
    win.focus_set()

    W, H = 600, 400
    canvas = tk.Canvas(win, width=W, height=H, bg="white")
    canvas.pack()

    # --- Mode settings ---
    levels = {
        "normal":   {"gravity": 0.2, "tap_power": 5},
        "mild":     {"gravity": 0.4, "tap_power": 4},
        "moderate": {"gravity": 0.6, "tap_power": 3},
        "severe":   {"gravity": 0.8, "tap_power": 2},
    }
    settings = levels.get(mode, levels["normal"])
    gravity = settings["gravity"]
    tap_power = settings["tap_power"]

    # --- State ---
    angle = 0
    score = 0
    running = False
    fail_limit = 70

    duration = Config.BALANCE_TEST_DURATION
    time_left = duration

    # --- Timer label ---
    timer_label = tk.Label(win, text=f"Time: {time_left}", font=("Arial", 12))
    timer_label.pack(pady=5)

    # --- Canvas setup ---
    canvas.create_line(W / 2, H / 2 - 70, W / 2, H / 2 + 70, width=3, fill="#ccc")
    bar_length = 120
    bar = canvas.create_line(W / 2, H / 2, W / 2, H / 2 - bar_length, width=10, fill="blue")

    controls_frame = None  # to hold reset and end buttons

    # --- Draw bar based on angle ---
    def draw_bar():
        x1, y1 = W / 2, H / 2
        x2 = x1 + bar_length * math.sin(math.radians(angle))
        y2 = y1 - bar_length * math.cos(math.radians(angle))
        canvas.coords(bar, x1, y1, x2, y2)

        tilt_ratio = abs(angle) / fail_limit
        color = "blue" if tilt_ratio < 0.5 else "orange" if tilt_ratio < 0.8 else "red"
        canvas.itemconfig(bar, fill=color)

    # --- Gravity sway ---
    def sway():
        nonlocal angle, score
        if not running:
            return
        if angle == 0:
            angle += random.choice([-1, 1]) * gravity
        else:
            angle += gravity * (1 + abs(angle) / 20) * (1 if angle > 0 else -1)
        angle = max(-90, min(90, angle))
        draw_bar()
        if abs(angle) >= fail_limit:
            fail_game()
            return
        score += max(0, fail_limit - abs(angle))
        win.after(50, sway)

    # --- Timer countdown ---
    def update_timer():
        nonlocal time_left
        if running:
            if time_left > 0:
                time_left -= 1
                timer_label.config(text=f"Time: {time_left}")
                win.after(1000, update_timer)
            else:
                end_game(auto=True)

    # --- Keyboard control ---
    def on_press(event):
        nonlocal angle
        if not running:
            return
        if event.keysym == "Left":
            angle -= tap_power
        elif event.keysym == "Right":
            angle += tap_power
        angle = max(-90, min(90, angle))
        draw_bar()
        if abs(angle) >= fail_limit:
            fail_game()

    # --- Stop and end logic ---
    def fail_game():
        nonlocal running
        if not running:
            return
        running = False
        messagebox.showwarning("You fell!", "You lost your balance!")
        show_end_controls()

    def end_game(auto=False):
        nonlocal running
        if not running:
            return
        running = False
        accuracy = score / 500
        upload_test(user_id, Config.BALANCE_TEST_DURATION, accuracy, mode)
        msg = "Time limit reached!" if auto else "Test completed."
        messagebox.showinfo("Balance Results", f"{msg}\nBalance accuracy: {accuracy:.1f}")
        show_end_controls()

    # --- Reset game ---
    def reset_game():
        nonlocal angle, score, running, time_left
        if controls_frame:
            controls_frame.destroy()
        angle = 0
        score = 0
        time_left = Config.BALANCE_TEST_DURATION
        timer_label.config(text=f"Time: {time_left}")
        draw_bar()
        start_game()

    # --- End test manually ---
    def end_test():
        running = False
        win.destroy()

    # --- Show reset + end buttons after finish/fail ---
    def show_end_controls():
        nonlocal controls_frame
        controls_frame = tk.Frame(win)
        controls_frame.pack(pady=10)

        tk.Button(
            controls_frame, text="Reset", width=10, bg="#007ACC", fg="white",
            font=("Arial", 10, "bold"), command=reset_game
        ).pack(side="left", padx=10)

        tk.Button(
            controls_frame, text="End Test", width=10, bg="#D9534F", fg="white",
            font=("Arial", 10, "bold"), command=end_test
        ).pack(side="left", padx=10)

    # --- Start immediately ---
    def start_game():
        nonlocal running
        running = True
        update_timer()
        sway()

    win.bind("<KeyPress>", on_press)
    draw_bar()
    start_game()
