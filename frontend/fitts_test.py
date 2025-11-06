import tkinter as tk
from tkinter import messagebox
import random, math, time, csv, os
from frontend.api_client import upload_test
from app.config import Config
from PIL import Image, ImageTk, ImageDraw

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)


def run_fitts_test(root, user_id, mode="normal"):
    win = tk.Toplevel(root)
    win.title(f"Fitts' Law Test ({mode.capitalize()})")

    W, H = Config.CANVAS_WIDTH, Config.CANVAS_HEIGHT
    canvas = tk.Canvas(win, width=W, height=H, bg="white")
    canvas.pack()

    mid_x, mid_y = W // 2, H // 2
    trial_index, results = 0, []
    target_id = None
    target_center, target_radius, start_time = None, None, None
    prev_click = [mid_x, mid_y]
    test_active = False

    levels = {
        "normal": {"delay_ms": 0, "jitter": 0},
        "mild": {"delay_ms": 100, "jitter": 5},
        "moderate": {"delay_ms": 300, "jitter": 10},
        "severe": {"delay_ms": 600, "jitter": 20},
    }
    params = levels.get(mode, levels["normal"])
    delay_ms, jitter = params["delay_ms"], params["jitter"]

    total_time = Config.FITTS_TEST_DURATION
    remaining = total_time
    timer_label = tk.Label(win, text=f"Time: {remaining}", font=("Arial", 12))
    timer_label.pack(pady=5)

    def update_timer():
        nonlocal remaining
        if not test_active:
            return
        if remaining > 0:
            remaining -= 1
            timer_label.config(text=f"Time: {remaining}")
            win.after(1000, update_timer)
        else:
            end_experiment(auto=True)

    def start_countdown():
        canvas.delete("all")

        def update(sec):
            canvas.delete("all")
            if sec >= 0:
                canvas.create_text(mid_x, mid_y, text=str(sec), font=("Helvetica", 40))
                win.after(1000, lambda: update(sec - 1))
            else:
                start_test()

        update(3)

    def start_test():
        nonlocal test_active
        test_active = True
        update_timer()
        next_trial()

    def next_trial():
        nonlocal trial_index, target_id, target_center, target_radius, start_time
        if not test_active:
            return
        if trial_index >= Config.NUM_TRIALS:
            end_experiment(auto=True)
            return

        canvas.delete("all")
        trial_index += 1
        target_radius = random.randint(Config.MIN_TARGET_RADIUS, Config.MAX_TARGET_RADIUS)
        cx = random.randint(target_radius, W - target_radius)
        cy = random.randint(target_radius, H - target_radius)
        target_id = canvas.create_oval(cx - target_radius, cy - target_radius,
                                       cx + target_radius, cy + target_radius,
                                       fill="blue", outline="")
        target_center = (cx, cy)
        start_time = time.time()

        if jitter > 0:
            overlay = Image.new("RGBA", (W, H), (255, 255, 255, 0))
            draw = ImageDraw.Draw(overlay)
            for _ in range(max(2, jitter // 3)):
                offset_x = random.randint(-target_radius, target_radius)
                offset_y = random.randint(-target_radius, target_radius)
                blur_r = int(target_radius * random.uniform(0.8, 1.2))
                color = (
                    random.randint(220, 255),
                    random.randint(220, 255),
                    random.randint(220, 255),
                    random.randint(120, 200)
                )
                draw.ellipse([(cx + offset_x) - blur_r, (cy + offset_y) - blur_r,
                              (cx + offset_x) + blur_r, (cy + offset_y) + blur_r],
                             fill=color)
            overlay_tk = ImageTk.PhotoImage(overlay)
            canvas.overlay_img = overlay_tk
            canvas.create_image(0, 0, image=overlay_tk, anchor="nw")

    def handle_click(event):
        if not test_active or target_center is None or start_time is None:
            return
        if delay_ms:
            win.after(delay_ms, lambda: process_click(event))
        else:
            process_click(event)

    def process_click(event):
        nonlocal prev_click, start_time
        if jitter:
            event.x += random.randint(-jitter, jitter)
            event.y += random.randint(-jitter, jitter)

        dist_prev = math.dist((event.x, event.y), prev_click)
        dist_center = math.dist((event.x, event.y), target_center)
        elapsed_ms = (time.time() - start_time) * 1000

        if dist_center <= target_radius and elapsed_ms > 0:
            results.append([trial_index, target_radius * 2, round(dist_prev, 2), round(elapsed_ms, 2)])
            prev_click = target_center
            next_trial()

    def end_experiment(auto=False):
        nonlocal test_active
        if not test_active:
            return
        test_active = False
        avg_time = sum(r[3] for r in results) / len(results) if results else 0
        accuracy = 100
        upload_test(user_id, avg_time, accuracy, mode)

        csv_name = os.path.join(DATA_DIR, f"fitts_{mode}.csv")
        with open(csv_name, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Trial", "Target Size (px)", "Distance (px)", "Time (ms)"])
            writer.writerows(results)

        msg = "Time limit reached!" if auto else "Test completed."
        messagebox.showinfo("Fitts' Law Results",
                            f"{msg}\nAverage time: {avg_time:.2f} ms\nData saved to {csv_name}")

    def close_test():
        end_experiment()
        win.destroy()

    tk.Button(win, text="End Test", command=close_test).pack(pady=10)
    canvas.bind("<Button-1>", handle_click)
    start_countdown()
