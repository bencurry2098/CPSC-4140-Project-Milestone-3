import tkinter as tk
from tkinter import messagebox
import random, math, time, csv, os
from frontend.api_client import upload_test
from app.config import Config
from PIL import Image, ImageTk, ImageDraw
from frontend.learn_popup import show_learn_popup

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)


def run_fitts_test(root, user_id, mode="normal"):
    win = tk.Toplevel(root)
    win.title(f"Fitts' Law Test ({mode.capitalize()})")
    win.configure(bg=Config.BG_COLOR)

    W, H = Config.CANVAS_WIDTH, Config.CANVAS_HEIGHT
    canvas = tk.Canvas(win, width=W, height=H, bg="white", highlightthickness=0)
    canvas.pack()

    mid_x, mid_y = W // 2, H // 2
    trial_index, results = 0, []
    target_center, target_radius, start_time = None, None, None
    target_id = None
    prev_click = [mid_x, mid_y]
    test_active = False

    # --- Impairment settings ---
    levels = {
        "normal":   {"delay_ms": 0,   "jitter": 0,  "reverse_chance": 0.0,  "sway_scale": 0},
        "mild":     {"delay_ms": 25,  "jitter": 10, "reverse_chance": 0.03, "sway_scale": 3},
        "moderate": {"delay_ms": 60,  "jitter": 20, "reverse_chance": 0.08, "sway_scale": 6},
        "severe":   {"delay_ms": 100, "jitter": 30, "reverse_chance": 0.12, "sway_scale": 8},
    }
    delay_ms = levels.get(mode, levels["normal"])["delay_ms"]
    jitter = levels.get(mode, levels["normal"])["jitter"]
    reverse_chance = levels.get(mode, levels["normal"])["reverse_chance"]
    sway_scale = levels.get(mode, levels["normal"])["sway_scale"]

    # --- Difficulty scaling (local adjustment only) ---
    base_min = Config.MIN_TARGET_RADIUS
    base_max = Config.MAX_TARGET_RADIUS

    if mode == "normal":
        min_r, max_r = base_min + 5, base_max + 5
    elif mode == "mild":
        min_r, max_r = base_min + 2, base_max + 2
    elif mode == "moderate":
        min_r, max_r = max(10, base_min - 5), max(15, base_max - 5)
    elif mode == "severe":
        min_r, max_r = max(8, base_min - 8), max(12, base_max - 8)
    else:
        min_r, max_r = base_min, base_max

    # --- UI ---
    control_frame = tk.Frame(win, bg=Config.BG_COLOR)
    control_frame.pack(pady=10)

    trial_label = tk.Label(
        control_frame,
        text=f"Trial: 0 / {Config.NUM_TRIALS}",
        font=("Helvetica", 12, "bold"),
        fg=Config.PRIMARY_COLOR,
        bg=Config.BG_COLOR
    )
    trial_label.pack(side="left", padx=10)

    tk.Button(
        control_frame,
        text="End Test",
        bg=Config.PRIMARY_COLOR,
        fg="white",
        font=("Helvetica", 11, "bold"),
        relief="flat",
        command=lambda: close_test(),
        width=12
    ).pack(side="right", padx=10)

    # --- Countdown ---
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

    # --- Start test ---
    def start_test():
        nonlocal test_active
        test_active = True
        next_trial()
        if mode != "normal":
            sway_target()

    # --- Next trial ---
    def next_trial():
        nonlocal trial_index, target_center, target_radius, start_time, target_id
        if not test_active:
            return
        if trial_index >= Config.NUM_TRIALS:
            end_experiment(auto=True)
            return

        canvas.delete("all")
        trial_index += 1
        trial_label.config(text=f"Trial: {trial_index} / {Config.NUM_TRIALS}")

        target_radius = random.randint(min_r, max_r)
        cx = random.randint(target_radius, W - target_radius)
        cy = random.randint(target_radius, H - target_radius)
        target_center = (cx, cy)

        # Main blue circle
        target_id = canvas.create_oval(
            cx - target_radius, cy - target_radius,
            cx + target_radius, cy + target_radius,
            fill="blue", outline=""
        )

        # --- Ghosting effect (closer cluster for severe mode) ---
        if mode == "severe":
            ghost_count = random.randint(2, 3)
            overlay = Image.new("RGBA", (W, H), (255, 255, 255, 0))
            draw = ImageDraw.Draw(overlay)

            # cluster ghosts within ±8px of the target center (was ±20)
            for _ in range(ghost_count):
                offset_x = random.randint(-8, 8)
                offset_y = random.randint(-8, 8)
                blur_r = int(target_radius * random.uniform(0.95, 1.05))
                color = (0, 0, 255, random.randint(70, 140))  # still semi-transparent
                draw.ellipse(
                    [
                        (cx + offset_x) - blur_r,
                        (cy + offset_y) - blur_r,
                        (cx + offset_x) + blur_r,
                        (cy + offset_y) + blur_r,
                    ],
                    fill=color,
                    outline=None
                )

            overlay_tk = ImageTk.PhotoImage(overlay)
            canvas.overlay_img = overlay_tk
            canvas.create_image(0, 0, image=overlay_tk, anchor="nw")

        start_time = time.time()

    # --- Handle Click (drift, reverse, delay) ---
    def handle_click(event):
        if not test_active or target_center is None:
            return

        x = canvas.canvasx(event.x)
        y = canvas.canvasy(event.y)

        # Simulate hand tremor drift
        x += random.uniform(-jitter, jitter)
        y += random.uniform(-jitter, jitter)

        # Random chance of reversed motion perception
        if reverse_chance > 0 and random.random() < reverse_chance:
            x, y = W - x, H - y

        # Apply delay effect
        if delay_ms:
            lag = delay_ms + random.randint(-delay_ms // 2, delay_ms // 2)
            win.after(max(0, lag), lambda: process_click(x, y))
        else:
            process_click(x, y)

    # --- Process Click ---
    def process_click(x, y):
        nonlocal prev_click, start_time
        if target_center is None:
            return

        cx, cy = target_center
        dist_center = math.dist((x, y), (cx, cy))
        dist_prev = math.dist((x, y), prev_click)
        elapsed = (time.time() - start_time) * 1000

        if dist_center <= target_radius + 1.5:
            results.append([trial_index, target_radius * 2, round(dist_prev, 2), round(elapsed, 2)])
            prev_click = target_center
            next_trial()

    # --- Target sway effect ---
    def sway_target():
        if not test_active or target_id is None:
            win.after(250, sway_target)
            return
        offset_x = random.randint(-sway_scale, sway_scale)
        offset_y = random.randint(-sway_scale, sway_scale)
        canvas.move(target_id, offset_x, offset_y)
        win.after(250, sway_target)

    # --- End Experiment ---
    def end_experiment(auto=False):
        nonlocal test_active
        if not test_active:
            return
        test_active = False
        avg_time = sum(r[3] for r in results) / len(results) if results else 0
        upload_test(user_id, avg_time, 100, mode)
        csv_name = os.path.join(DATA_DIR, f"fitts_{mode}.csv")
        with open(csv_name, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Trial", "Target Size (px)", "Distance (px)", "Time (ms)"])
            writer.writerows(results)
        msg = "All trials completed!" if auto else "Test ended."
        messagebox.showinfo(
            "Fitts' Law Results",
            f"{msg}\nAverage time: {avg_time:.2f} ms\n\nData saved to:\n{csv_name}"
        )
        show_learn_popup(win, "fitts", mode)

    def close_test():
        end_experiment()
        win.destroy()

    canvas.bind("<Button-1>", handle_click)
    start_countdown()
