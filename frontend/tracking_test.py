import tkinter as tk
import random, time, math
from tkinter import messagebox
from frontend.api_client import upload_test
from app.config import Config


def run_target_tracking(root, user_id, mode="normal"):
    win = tk.Toplevel(root)
    win.title(f"Target Tracking Test ({mode.capitalize()})")
    win.configure(bg=Config.BG_COLOR)

    W, H = Config.CANVAS_WIDTH, Config.CANVAS_HEIGHT
    canvas = tk.Canvas(win, width=W, height=H, bg="white")
    canvas.pack()

    # --- Mode parameters ---
    params = {
        "normal": {"speed": 3, "wobble": 0},
        "mild": {"speed": 3, "wobble": 2},
        "moderate": {"speed": 2.5, "wobble": 5},
        "severe": {"speed": 2, "wobble": 9},
    }
    speed, wobble = params.get(mode, params["normal"]).values()

    target_radius = 40
    cx, cy = W // 2, H // 2
    dx, dy = random.choice([-1, 1]) * speed, random.choice([-1, 1]) * speed
    target_id = None  # will be created later

    duration, time_left = Config.TRACKING_TEST_DURATION, Config.TRACKING_TEST_DURATION
    timer_label = tk.Label(win, text=f"Time: {time_left}", font=("Helvetica", 12, "bold"),
                           fg=Config.PRIMARY_COLOR, bg=Config.BG_COLOR)
    timer_label.pack(pady=5)

    tracking_start, mouse_positions = None, []
    test_running = False

    # --- Timer update ---
    def update_timer():
        nonlocal time_left, test_running
        if not test_running:
            return
        if time_left > 0:
            time_left -= 1
            timer_label.config(text=f"Time: {time_left}")
            win.after(1000, update_timer)
        else:
            end_test(auto=True)

    # --- Target motion ---
    def move_target():
        nonlocal cx, cy, dx, dy, test_running
        if not test_running:
            return

        cx += dx
        cy += dy
        if cx - target_radius <= 0 or cx + target_radius >= W:
            dx *= -1
        if cy - target_radius <= 0 or cy + target_radius >= H:
            dy *= -1

        wx = random.randint(-wobble, wobble)
        wy = random.randint(-wobble, wobble)
        wr = target_radius + random.randint(-wobble // 2, wobble // 2)

        canvas.coords(target_id, cx - wr + wx, cy - wr + wy, cx + wr + wx, cy + wr + wy)
        win.after(30, move_target)

    # --- Mouse tracking ---
    def track_mouse(event):
        if tracking_start:
            dist = math.dist((event.x, event.y), (cx, cy))
            mouse_positions.append(dist)

    canvas.bind("<Motion>", track_mouse)

    # --- Countdown before start ---
    def start_countdown(sec=3):
        canvas.delete("all")
        if sec >= 0:
            canvas.create_text(W / 2, H / 2, text=str(sec), font=("Helvetica", 40))
            win.after(1000, lambda: start_countdown(sec - 1))
        else:
            start_test()

    # --- Start test ---
    def start_test():
        nonlocal tracking_start, target_id, test_running
        canvas.delete("all")
        target_id = canvas.create_oval(cx - target_radius, cy - target_radius,
                                       cx + target_radius, cy + target_radius,
                                       fill="red", outline="")
        tracking_start = time.time()
        test_running = True
        update_timer()
        move_target()

    # --- End test ---
    def end_test(auto=False):
        nonlocal test_running
        if not tracking_start:
            return
        test_running = False
        elapsed = time.time() - tracking_start
        avg_distance = sum(mouse_positions) / len(mouse_positions) if mouse_positions else 0
        accuracy = max(0, 100 - min(avg_distance / 5, 100))
        upload_test(user_id, elapsed, accuracy, mode)

        msg = "Time up!" if auto else "Test ended."
        messagebox.showinfo(
            "Tracking Results",
            f"{msg}\nTotal time: {elapsed:.1f}s\nAverage distance: {avg_distance:.1f}px"
        )

        # Show Learn popup before closing
        from frontend.learn_popup import show_learn_popup
        show_learn_popup(root, "tracking")

        win.destroy()  # Close test window after showing results

    # --- Controls ---
    tk.Button(
        win,
        text="End Test",
        bg=Config.PRIMARY_COLOR,
        fg="white",
        font=("Helvetica", 11, "bold"),
        relief="flat",
        command=end_test
    ).pack(pady=10)

    # --- Run ---
    start_countdown()
