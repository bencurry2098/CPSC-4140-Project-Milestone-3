import tkinter as tk
import random, time, math
from tkinter import messagebox
from frontend.api_client import upload_test
from app.config import Config


def run_target_tracking(root, user_id, mode="normal"):
    win = tk.Toplevel(root)
    win.title(f"Target Tracking Test ({mode.capitalize()})")

    W, H = Config.CANVAS_WIDTH, Config.CANVAS_HEIGHT
    canvas = tk.Canvas(win, width=W, height=H, bg="white")
    canvas.pack()

    target_radius = 40
    cx, cy = W // 2, H // 2

    params = {
        "normal": {"speed": 3, "wobble": 0},
        "mild": {"speed": 3, "wobble": 2},
        "moderate": {"speed": 2.5, "wobble": 5},
        "severe": {"speed": 2, "wobble": 9},
    }
    settings = params.get(mode, params["normal"])
    speed, wobble = settings["speed"], settings["wobble"]
    dx, dy = random.choice([-1, 1]) * speed, random.choice([-1, 1]) * speed

    target_id = canvas.create_oval(cx - target_radius, cy - target_radius,
                                   cx + target_radius, cy + target_radius,
                                   fill="red", outline="")

    tracking_start = None
    mouse_positions = []
    test_active = False

    duration = Config.TRACKING_TEST_DURATION
    time_left = duration
    timer_label = tk.Label(win, text=f"Time: {time_left}", font=("Arial", 12))
    timer_label.pack(pady=5)

    def update_timer():
        nonlocal time_left
        if not test_active:
            return
        if time_left > 0:
            time_left -= 1
            timer_label.config(text=f"Time: {time_left}")
            win.after(1000, update_timer)
        else:
            stop_test(auto=True)

    def move_target():
        nonlocal cx, cy, dx, dy
        if not test_active:
            return

        cx += dx
        cy += dy
        if cx - target_radius <= 0 or cx + target_radius >= W:
            dx *= -1
        if cy - target_radius <= 0 or cy + target_radius >= H:
            dy *= -1

        wobble_x = random.randint(-wobble, wobble)
        wobble_y = random.randint(-wobble, wobble)
        wobble_r = target_radius + random.randint(-wobble // 2, wobble // 2)

        canvas.coords(target_id,
                      cx - wobble_r + wobble_x,
                      cy - wobble_r + wobble_y,
                      cx + wobble_r + wobble_x,
                      cy + wobble_r + wobble_y)

        win.after(30, move_target)

    def track_mouse(event):
        if tracking_start and test_active:
            dist = math.dist((event.x, event.y), (cx, cy))
            mouse_positions.append(dist)

    canvas.bind("<Motion>", track_mouse)

    def start_countdown(sec=3):
        canvas.delete("all")
        if sec >= 0:
            canvas.create_text(W / 2, H / 2, text=str(sec), font=("Helvetica", 40))
            win.after(1000, lambda: start_countdown(sec - 1))
        else:
            start_test()

    def start_test():
        nonlocal tracking_start, target_id, test_active
        canvas.delete("all")
        target_id = canvas.create_oval(cx - target_radius, cy - target_radius,
                                       cx + target_radius, cy + target_radius,
                                       fill="red", outline="")
        tracking_start = time.time()
        test_active = True
        update_timer()
        move_target()

    def stop_test(auto=False):
        nonlocal test_active
        if not test_active:
            return
        test_active = False
        elapsed = time.time() - tracking_start if tracking_start else 0
        avg_distance = sum(mouse_positions) / len(mouse_positions) if mouse_positions else 0
        accuracy = max(0, 100 - min(avg_distance / 5, 100))
        upload_test(user_id, elapsed, accuracy, mode)
        msg = "Time limit reached!" if auto else "Test completed."
        messagebox.showinfo("Tracking Results",
                            f"{msg}\nTime: {elapsed:.1f}s\nAvg distance: {avg_distance:.1f}px")

    def end_test():
        stop_test()
        win.destroy()

    tk.Button(win, text="End Test", command=end_test).pack(pady=10)
    start_countdown()
