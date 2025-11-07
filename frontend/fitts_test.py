import tkinter as tk
from tkinter import messagebox
import random, math, time, csv, os
from frontend.api_client import upload_test
from app.config import Config
from PIL import Image, ImageTk, ImageDraw
from frontend.learn_popup import show_learn_popup

# Create data directory if it doesn't exist
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Fitts' Law Test
def run_fitts_test(root, user_id, impairment_level="normal"):
    window = tk.Toplevel(root)
    window.title(f"Fitts' Law Test ({impairment_level.capitalize()})")
    window.configure(bg=Config.BG_COLOR)

    canvas_width, canvas_height = Config.CANVAS_WIDTH, Config.CANVAS_HEIGHT
    canvas = tk.Canvas(window, width=canvas_width, height=canvas_height, bg="white", highlightthickness=0)
    canvas.pack()

    center_x, center_y = canvas_width // 2, canvas_height // 2
    current_trial_index, trial_results = 0, []
    current_target_center, current_target_radius, click_start_time = None, None, None
    current_target_id = None
    previous_click_position = [center_x, center_y]
    test_is_active = False

    # Impairment simulation settings
    impairment_parameters = {
        "normal":   {"delay_ms": 0,   "jitter": 0,  "reverse_chance": 0.0,  "sway_scale": 0},
        "mild":     {"delay_ms": 25,  "jitter": 10, "reverse_chance": 0.03, "sway_scale": 3},
        "moderate": {"delay_ms": 60,  "jitter": 20, "reverse_chance": 0.08, "sway_scale": 6},
        "severe":   {"delay_ms": 100, "jitter": 30, "reverse_chance": 0.12, "sway_scale": 8},
    }
    input_delay_ms = impairment_parameters.get(impairment_level, impairment_parameters["normal"])["delay_ms"]
    input_jitter = impairment_parameters.get(impairment_level, impairment_parameters["normal"])["jitter"]
    motion_reversal_chance = impairment_parameters.get(impairment_level, impairment_parameters["normal"])["reverse_chance"]
    sway_intensity = impairment_parameters.get(impairment_level, impairment_parameters["normal"])["sway_scale"]

    # Difficulty scaling
    base_min_radius = Config.MIN_TARGET_RADIUS
    base_max_radius = Config.MAX_TARGET_RADIUS

    if impairment_level == "normal":
        min_radius, max_radius = base_min_radius + 5, base_max_radius + 5
    elif impairment_level == "mild":
        min_radius, max_radius = base_min_radius + 2, base_max_radius + 2
    elif impairment_level == "moderate":
        min_radius, max_radius = max(10, base_min_radius - 5), max(15, base_max_radius - 5)
    elif impairment_level == "severe":
        min_radius, max_radius = max(8, base_min_radius - 8), max(12, base_max_radius - 8)
    else:
        min_radius, max_radius = base_min_radius, base_max_radius

    # UI
    control_frame = tk.Frame(window, bg=Config.BG_COLOR)
    control_frame.pack(pady=10)

    trial_progress_label = tk.Label(
        control_frame,
        text=f"Trial: 0 / {Config.NUM_TRIALS}",
        font=("Helvetica", 12, "bold"),
        fg=Config.PRIMARY_COLOR,
        bg=Config.BG_COLOR
    )
    trial_progress_label.pack(side="left", padx=10)

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

    # Countdown
    def start_countdown():
        canvas.delete("all")

        def update_countdown(seconds_remaining):
            canvas.delete("all")
            if seconds_remaining >= 0:
                canvas.create_text(center_x, center_y, text=str(seconds_remaining), font=("Helvetica", 40))
                window.after(1000, lambda: update_countdown(seconds_remaining - 1))
            else:
                start_test()

        update_countdown(3)

    # Start test
    def start_test():
        nonlocal test_is_active
        test_is_active = True
        start_next_trial()
        if impairment_level != "normal":
            sway_target_position()

    # Next trial
    def start_next_trial():
        nonlocal current_trial_index, current_target_center, current_target_radius, click_start_time, current_target_id
        if not test_is_active:
            return
        if current_trial_index >= Config.NUM_TRIALS:
            end_experiment(auto=True)
            return

        canvas.delete("all")
        current_trial_index += 1
        trial_progress_label.config(text=f"Trial: {current_trial_index} / {Config.NUM_TRIALS}")

        current_target_radius = random.randint(min_radius, max_radius)
        target_center_x = random.randint(current_target_radius, canvas_width - current_target_radius)
        target_center_y = random.randint(current_target_radius, canvas_height - current_target_radius)
        current_target_center = (target_center_x, target_center_y)

        # Main blue circle
        current_target_id = canvas.create_oval(
            target_center_x - current_target_radius, target_center_y - current_target_radius,
            target_center_x + current_target_radius, target_center_y + current_target_radius,
            fill="blue", outline=""
        )

        # Ghosting effect (for severe mode)
        if impairment_level == "severe":
            ghost_count = random.randint(2, 3)
            overlay_image = Image.new("RGBA", (canvas_width, canvas_height), (255, 255, 255, 0))
            overlay_draw = ImageDraw.Draw(overlay_image)

            for _ in range(ghost_count):
                offset_x = random.randint(-8, 8)
                offset_y = random.randint(-8, 8)
                blurred_radius = int(current_target_radius * random.uniform(0.95, 1.05))
                ghost_color = (0, 0, 255, random.randint(70, 140))
                overlay_draw.ellipse(
                    [(target_center_x + offset_x) - blurred_radius,
                     (target_center_y + offset_y) - blurred_radius,
                     (target_center_x + offset_x) + blurred_radius,
                     (target_center_y + offset_y) + blurred_radius],
                    fill=ghost_color,
                    outline=None
                )

            overlay_tk_image = ImageTk.PhotoImage(overlay_image)
            canvas.overlay_img = overlay_tk_image
            canvas.create_image(0, 0, image=overlay_tk_image, anchor="nw")

        click_start_time = time.time()

    # Handle Click (drift, reverse, delay)
    def handle_click(event):
        if not test_is_active or current_target_center is None:
            return

        click_x = canvas.canvasx(event.x)
        click_y = canvas.canvasy(event.y)

        # Simulate hand tremor drift
        click_x += random.uniform(-input_jitter, input_jitter)
        click_y += random.uniform(-input_jitter, input_jitter)

        # Random chance of reversed motion
        if motion_reversal_chance > 0 and random.random() < motion_reversal_chance:
            click_x, click_y = canvas_width - click_x, canvas_height - click_y

        # Apply delay effect
        if input_delay_ms:
            delay = input_delay_ms + random.randint(-input_delay_ms // 2, input_delay_ms // 2)
            window.after(max(0, delay), lambda: process_click(click_x, click_y))
        else:
            process_click(click_x, click_y)

    # Process Click
    def process_click(click_x, click_y):
        nonlocal previous_click_position, click_start_time
        if current_target_center is None:
            return

        target_center_x, target_center_y = current_target_center
        distance_to_target_center = math.dist((click_x, click_y), (target_center_x, target_center_y))
        distance_from_previous_click = math.dist((click_x, click_y), previous_click_position)
        reaction_time_ms = (time.time() - click_start_time) * 1000

        if distance_to_target_center <= current_target_radius + 1.5:
            trial_results.append([
                current_trial_index,
                current_target_radius * 2,
                round(distance_from_previous_click, 2),
                round(reaction_time_ms, 2)
            ])
            previous_click_position = current_target_center
            start_next_trial()

    # Target sway effect
    def sway_target_position():
        if not test_is_active or current_target_id is None:
            window.after(250, sway_target_position)
            return
        offset_x = random.randint(-sway_intensity, sway_intensity)
        offset_y = random.randint(-sway_intensity, sway_intensity)
        canvas.move(current_target_id, offset_x, offset_y)
        window.after(250, sway_target_position)

    # End Experiment
    def end_experiment(auto=False):
        nonlocal test_is_active
        if not test_is_active:
            return
        test_is_active = False
        average_reaction_time = sum(record[3] for record in trial_results) / len(trial_results) if trial_results else 0
        upload_test(user_id, average_reaction_time, 100, impairment_level)
        csv_filename = os.path.join(DATA_DIR, f"fitts_{impairment_level}.csv")
        with open(csv_filename, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Trial", "Target Size (px)", "Distance (px)", "Time (ms)"])
            writer.writerows(trial_results)
        message_text = "All trials completed!" if auto else "Test ended."
        messagebox.showinfo(
            "Fitts' Law Results",
            f"{message_text}\nAverage time: {average_reaction_time:.2f} ms\n\nData saved to:\n{csv_filename}"
        )
        show_learn_popup(window, "fitts", impairment_level)

    def close_test():
        end_experiment()
        window.destroy()

    canvas.bind("<Button-1>", handle_click)
    messagebox.showinfo("How to Play", "Click on the blue circle")
    window.lift()
    window.focus_force()
    start_countdown()
