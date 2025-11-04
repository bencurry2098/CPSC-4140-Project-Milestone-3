import tkinter as tk
from tkinter import messagebox
import random, math, time
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
    gravity = settings["gravity"]        # automatic tilt per frame
    tap_power = settings["tap_power"]    # how much each key tap moves the bar

    # --- Game state ---
    angle = 0
    score = 0
    running = True
    fail_limit = 70

    # --- Reference and bar ---
    canvas.create_line(W/2, H/2-70, W/2, H/2+70, width=3, fill="#ccc")
    bar_length = 120
    bar = canvas.create_line(W/2, H/2, W/2, H/2 - bar_length, width=10, fill="blue")

    def draw_bar():
        x1, y1 = W/2, H/2
        x2 = x1 + bar_length * math.sin(math.radians(angle))
        y2 = y1 - bar_length * math.cos(math.radians(angle))
        canvas.coords(bar, x1, y1, x2, y2)

        tilt_ratio = abs(angle) / fail_limit
        if tilt_ratio < 0.5:
            color = "blue"
        elif tilt_ratio < 0.8:
            color = "orange"
        else:
            color = "red"
        canvas.itemconfig(bar, fill=color)

    def sway():
        nonlocal angle, score, running
        if not running:
            return

        # Gravity pulls the bar in the direction it's leaning
        if angle == 0:
            angle += random.choice([-1,1]) * gravity  # small random nudge if perfectly centered
        else:
            angle += gravity * (1 + abs(angle)/20) * (1 if angle > 0 else -1)

        # Clamp and redraw
        angle = max(-90, min(90, angle))
        draw_bar()

        # Fail check
        if abs(angle) >= fail_limit:
            fail_game()
            return

        # Scoring
        score += max(0, fail_limit - abs(angle))
        win.after(50, sway)


    def on_press(event):
        """Apply tap to fight gravity."""
        nonlocal angle
        if event.keysym == "Left":
            angle -= tap_power
        elif event.keysym == "Right":
            angle += tap_power

        angle = max(-90, min(90, angle))
        draw_bar()

        if abs(angle) >= fail_limit:
            fail_game()

    def fail_game():
        nonlocal running
        running = False
        messagebox.showwarning("You fell!", "You lost your balance!")
        win.destroy()

    def end_game():
        nonlocal running
        if not running:
            return
        running = False
        accuracy = score / 500
        upload_test(user_id, 15, accuracy, mode)
        messagebox.showinfo("Result", f"Balance accuracy: {accuracy:.1f}")
        win.destroy()

    win.bind("<KeyPress>", on_press)
    draw_bar()
    sway()
    win.after(15000, end_game)
