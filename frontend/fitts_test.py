import tkinter as tk
from tkinter import messagebox
import random, math, time, csv, os
from frontend.api_client import upload_test
from app.config import Config
from PIL import Image, ImageTk, ImageDraw

# ensure a /data directory exists at project root
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)


def run_fitts_test(root, user_id, mode="normal"):
    """Fitts’ Law experiment window."""
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

    # impairment simulation parameters
    if mode in ["normal", "simulated", "mild", "moderate", "severe"]:
        levels = {
            "normal":  {"delay_ms": 0, "jitter": 0},
            "simulated": {"delay_ms": 150, "jitter": 8},  # legacy
            "mild": {"delay_ms": 100, "jitter": 5},
            "moderate": {"delay_ms": 300, "jitter": 10},
            "severe": {"delay_ms": 600, "jitter": 20},
        }
        params = levels.get(mode, levels["normal"])
        delay_ms, jitter = params["delay_ms"], params["jitter"]
    else:
        delay_ms, jitter = 0, 0

    # countdown before test
    def start_countdown():
        canvas.delete("all")

        def update(sec):
            canvas.delete("all")
            if sec >= 0:
                canvas.create_text(mid_x, mid_y, text=str(sec), font=("Helvetica", 40))
                win.after(1000, lambda: update(sec - 1))
            else:
                next_trial()

        update(3)

    # create next target
    def next_trial():
        nonlocal trial_index, target_id, target_center, target_radius, start_time
        if trial_index >= Config.NUM_TRIALS:
            end_experiment()
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

        # add blur effect
        # --- create a transparent overlay image ---
        if jitter > 0:
            blur_count = max(2, jitter // 3)

            # Create a transparent RGBA image same size as canvas
            overlay = Image.new("RGBA", (W, H), (255, 255, 255, 0))
            draw = ImageDraw.Draw(overlay)

            for _ in range(blur_count):
                offset_x = random.randint(-target_radius, target_radius)
                offset_y = random.randint(-target_radius, target_radius)
                blur_r = int(target_radius * random.uniform(0.8, 1.2))

                # Random pale color with transparency (alpha 50–120)
                color = (
                    random.randint(220, 255),
                    random.randint(220, 255),
                    random.randint(220, 255),
                    random.randint(120, 200)
                )
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

            # Convert Pillow image to Tk image and display it
            overlay_tk = ImageTk.PhotoImage(overlay)
            canvas.overlay_img = overlay_tk  # keep reference so it's not garbage collected
            canvas.create_image(0, 0, image=overlay_tk, anchor="nw")
        # ---------

    # handle mouse click
    def handle_click(event):
        if target_center is None or start_time is None:
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
            results.append([
                trial_index,
                target_radius * 2,
                round(dist_prev, 2),
                round(elapsed_ms, 2)
            ])
            prev_click = target_center
            next_trial()

    def end_experiment():
        canvas.delete("all")
        canvas.create_text(mid_x, mid_y, text="Experiment Complete", font=("Helvetica", 20))
        avg_time = sum(r[3] for r in results) / len(results)
        accuracy = 100
        upload_test(user_id, avg_time, accuracy, mode)

        # save to /data directory
        csv_name = os.path.join(DATA_DIR, f"fitts_{mode}.csv")
        with open(csv_name, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Trial", "Target Size (px)", "Distance (px)", "Time (ms)"])
            writer.writerows(results)

        messagebox.showinfo("Done", f"Average time: {avg_time:.2f} ms\nData saved to {csv_name}")

    canvas.bind("<Button-1>", handle_click)
    start_countdown()
