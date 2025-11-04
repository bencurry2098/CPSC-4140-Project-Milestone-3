import tkinter as tk
from tkinter import messagebox
import random, math, time
from frontend.api_client import upload_test
from app.config import Config

def run_balance_game(root, user_id, mode="normal"):
    win = tk.Toplevel(root)
    win.title(f"Balance Game ({mode.capitalize()})")

    W, H = 600, 400
    canvas = tk.Canvas(win, width=W, height=H, bg="white")
    canvas.pack()

    # --- Mode settings ---
    levels = {
        "normal":   {"sway": 0.5, "delay": 0,   "wobble": 0.5},
        "mild":     {"sway": 1.0, "delay": 100, "wobble": 1.5},
        "moderate": {"sway": 2.0, "delay": 200, "wobble": 3.0},
        "severe":   {"sway": 3.0, "delay": 400, "wobble": 5.0},
    }
    settings = levels.get(mode, levels["normal"])
    sway_strength = settings["sway"]
    delay = settings["delay"]
    wobble = settings["wobble"]

    # --- Game state ---
    angle = 0
    score = 0
    running = True
    pressed_keys = {"Left": False, "Right": False}
    fail_limit = 70  # easier fail threshold

    # --- Reference and bar ---
    canvas.create_line(W/2, H/2-70, W/2, H/2+70, width=3, fill="#ccc")
    bar_length = 120
    bar = canvas.create_line(W/2, H/2, W/2, H/2 - bar_length, width=10, fill="blue")

    def draw_bar():
        """Redraw the bar based on current angle."""
        x1, y1 = W/2, H/2
        x2 = x1 + bar_length * math.sin(math.radians(angle))
        y2 = y1 - bar_length * math.cos(math.radians(angle))
        canvas.coords(bar, x1, y1, x2, y2)

        # Gradually change color based on tilt
        tilt_ratio = abs(angle) / fail_limit
        if tilt_ratio < 0.5:
            color = "blue"
        elif tilt_ratio < 0.8:
            color = "orange"
        else:
            color = "red"
        canvas.itemconfig(bar, fill=color)

    def sway():
        """Simulate environment wobble and apply controls."""
        nonlocal angle, score, running
        if not running:
            return

        # Random sway and oscillation (instability)
        angle += random.uniform(-sway_strength, sway_strength)
        angle += math.sin(time.time() * wobble) * 0.5

        # Continuous movement if keys are held
        if pressed_keys["Left"]:
            angle -= 2
        if pressed_keys["Right"]:
            angle += 2

        # Clamp the angle range
        angle = max(-90, min(90, angle))
        draw_bar()

        # Check fail condition
        if abs(angle) >= fail_limit:
            fail_game()
            return

        # Scoring logic
        score += max(0, fail_limit - abs(angle))
        win.after(50, sway)

    def on_press(event):
        """Track when a key is pressed."""
        if event.keysym in pressed_keys:
            pressed_keys[event.keysym] = True

    def on_release(event):
        """Track when a key is released."""
        if event.keysym in pressed_keys:
            pressed_keys[event.keysym] = False

    def fail_game():
        """End immediately if bar tilts too far."""
        nonlocal running
        running = False
        messagebox.showwarning("You fell!", "You lost your balance!")
        win.destroy()

    def end_game():
        """End after timer runs out."""
        nonlocal running
        if not running:
            return
        running = False
        accuracy = score / 500  # normalized
        upload_test(user_id, 15, accuracy, mode)
        messagebox.showinfo("Result", f"Balance accuracy: {accuracy:.1f}")
        win.destroy()

    # Bind key events
    win.bind("<KeyPress>", on_press)
    win.bind("<KeyRelease>", on_release)

    draw_bar()
    sway()
    win.after(15000, end_game)
