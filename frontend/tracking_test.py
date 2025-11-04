import tkinter as tk
import random, time
from tkinter import messagebox
from frontend.api_client import upload_test
from app.config import Config

def run_target_tracking(root, user_id, mode="normal"):
    """Target tracking simulation — follow a moving target with your mouse."""
    win = tk.Toplevel(root)
    win.title(f"Target Tracking Test ({mode.capitalize()})")

    W, H = Config.CANVAS_WIDTH, Config.CANVAS_HEIGHT
    canvas = tk.Canvas(win, width=W, height=H, bg="white")
    canvas.pack()

    # --- Parameters ---
    target_radius = 35
    cx, cy = W // 2, H // 2

    # Mode settings
    params = {
        "normal":   {"speed": 3, "jitter": 0,  "blur": 0},
        "mild":     {"speed": 4, "jitter": 3,  "blur": 1},
        "moderate": {"speed": 5, "jitter": 6,  "blur": 2},
        "severe":   {"speed": 7, "jitter": 10, "blur": 3},
    }
    speed = params.get(mode, params["normal"])["speed"]
    jitter = params.get(mode, params["normal"])["jitter"]
    blur_strength = params.get(mode, params["normal"])["blur"]

    dx = random.choice([-1, 1]) * speed
    dy = random.choice([-1, 1]) * speed

    # Create the main target
    target_id = canvas.create_oval(cx - target_radius, cy - target_radius,
                                   cx + target_radius, cy + target_radius,
                                   fill="red", outline="")

    tracking_start = time.time()
    mouse_positions = []

    # --- Optional blur overlay ---
    def draw_blur(x, y):
        if blur_strength <= 0:
            return
        for _ in range(blur_strength * 2):
            offset_x = random.randint(-blur_strength * 3, blur_strength * 3)
            offset_y = random.randint(-blur_strength * 3, blur_strength * 3)
            color = f"#{random.randint(220,255):02x}{random.randint(220,255):02x}{random.randint(220,255):02x}"
            canvas.create_oval(
                (x + offset_x) - target_radius,
                (y + offset_y) - target_radius,
                (x + offset_x) + target_radius,
                (y + offset_y) + target_radius,
                fill=color,
                outline=color
            )

    # --- Smooth motion update ---
    def move_target():
        nonlocal cx, cy, dx, dy

        cx += dx
        cy += dy

        # bounce off walls
        if cx - target_radius <= 0 or cx + target_radius >= W:
            dx *= -1
        if cy - target_radius <= 0 or cy + target_radius >= H:
            dy *= -1

        # apply random jitter (impairment effect)
        if jitter > 0 and random.random() < 0.2:
            cx += random.randint(-jitter, jitter)
            cy += random.randint(-jitter, jitter)

        draw_blur(cx, cy)

        canvas.coords(target_id, cx - target_radius, cy - target_radius,
                      cx + target_radius, cy + target_radius)

        # clear old blur trails
        if canvas.find_all().__len__() > 5:
            canvas.delete(canvas.find_all()[0])

        win.after(25, move_target)

    # --- Track mouse distance from target ---
    def track_mouse(event):
        dist = ((event.x - cx) ** 2 + (event.y - cy) ** 2) ** 0.5
        mouse_positions.append(dist)

    canvas.bind("<Motion>", track_mouse)

    # --- End game after 20 seconds ---
    def end_test():
        avg_distance = sum(mouse_positions) / len(mouse_positions) if mouse_positions else 0
        total_time = time.time() - tracking_start

        upload_test(user_id, total_time, 100 - min(avg_distance / 5, 100), mode)

        messagebox.showinfo(
            "Tracking Complete",
            f"Time: {total_time:.1f}s\nAverage distance from target: {avg_distance:.1f}px"
        )
        win.destroy()

    move_target()
    win.after(20000, end_test)
