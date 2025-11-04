import tkinter as tk
import random, time, math
from tkinter import messagebox
from frontend.api_client import upload_test
from app.config import Config


def run_target_tracking(root, user_id, mode="normal"):
    """Target tracking simulation — follow a moving target with wobble impairment."""
    win = tk.Toplevel(root)
    win.title(f"Target Tracking Test ({mode.capitalize()})")

    W, H = Config.CANVAS_WIDTH, Config.CANVAS_HEIGHT
    canvas = tk.Canvas(win, width=W, height=H, bg="white")
    canvas.pack()

    # --- Parameters ---
    target_radius = 40
    cx, cy = W // 2, H // 2

    # Mode settings (speed + wobble intensity)
    params = {
        "normal":   {"speed": 3, "wobble": 0},
        "mild":     {"speed": 3, "wobble": 2},
        "moderate": {"speed": 2.5, "wobble": 5},
        "severe":   {"speed": 2, "wobble": 9},
    }
    settings = params.get(mode, params["normal"])
    speed = settings["speed"]
    wobble = settings["wobble"]

    dx = random.choice([-1, 1]) * speed
    dy = random.choice([-1, 1]) * speed

    # Create main target
    target_id = canvas.create_oval(cx - target_radius, cy - target_radius,
                                   cx + target_radius, cy + target_radius,
                                   fill="red", outline="")

    tracking_start = time.time()
    mouse_positions = []

    # --- Movement update with wobble effect ---
    def move_target():
        nonlocal cx, cy, dx, dy

        cx += dx
        cy += dy

        # Bounce off walls
        if cx - target_radius <= 0 or cx + target_radius >= W:
            dx *= -1
        if cy - target_radius <= 0 or cy + target_radius >= H:
            dy *= -1

        # Apply wobble (simulate distortion / shaking)
        wobble_x = random.randint(-wobble, wobble)
        wobble_y = random.randint(-wobble, wobble)
        wobble_r = target_radius + random.randint(-wobble // 2, wobble // 2)

        canvas.coords(target_id,
                      cx - wobble_r + wobble_x,
                      cy - wobble_r + wobble_y,
                      cx + wobble_r + wobble_x,
                      cy + wobble_r + wobble_y)

        win.after(30, move_target)

    # --- Track mouse distance from target ---
    def track_mouse(event):
        dist = math.dist((event.x, event.y), (cx, cy))
        mouse_positions.append(dist)

    canvas.bind("<Motion>", track_mouse)

    # --- End test after 20 seconds ---
    def end_test():
        avg_distance = sum(mouse_positions) / len(mouse_positions) if mouse_positions else 0
        total_time = time.time() - tracking_start
        accuracy = max(0, 100 - min(avg_distance / 5, 100))

        upload_test(user_id, total_time, accuracy, mode)
        messagebox.showinfo(
            "Tracking Complete",
            f"Time: {total_time:.1f}s\nAverage distance from target: {avg_distance:.1f}px"
        )
        win.destroy()

    move_target()
    win.after(20000, end_test)
