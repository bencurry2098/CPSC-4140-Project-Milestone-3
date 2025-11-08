import tkinter as tk
import random, time, math
from tkinter import messagebox
from frontend.api_client import upload_test
from app.config import Config

# runs the test and sets the default impairment level to normal
def run_target_tracking(parent_window, user_id, impairment_level="normal"):
    # create window for the test
    tracking_window = tk.Toplevel(parent_window)
    tracking_window.title(f"Target Tracking Test ({impairment_level.capitalize()})")
    tracking_window.configure(bg=Config.BG_COLOR)
    
    # setup inner window for the test
    canvas_width, canvas_height = Config.CANVAS_WIDTH, Config.CANVAS_HEIGHT
    canvas = tk.Canvas(tracking_window, width=canvas_width, height=canvas_height, bg="white")
    canvas.pack()

    # impairment levels and effects
    impairment_parameters = {
        "normal": {"speed": 3, "wobble": 0},
        "mild": {"speed": 3, "wobble": 2},
        "moderate": {"speed": 2.5, "wobble": 5},
        "severe": {"speed": 2, "wobble": 9},
    }

    # target variables
    target_speed, target_wobble = impairment_parameters.get(impairment_level, impairment_parameters["normal"]).values()
    target_radius = 40
    target_center_x, target_center_y = canvas_width // 2, canvas_height // 2
    target_shape_id = None

    # determine a random velocity
    target_velocity_x, target_velocity_y = random.choice([-1, 1]) * target_speed, random.choice([-1, 1]) * target_speed
    
    # displays timer for user to see
    _, time_remaining = Config.TRACKING_TEST_DURATION, Config.TRACKING_TEST_DURATION
    timer_label = tk.Label(tracking_window, text=f"Time: {time_remaining}", font=("Helvetica", 12, "bold"),
                           fg=Config.PRIMARY_COLOR, bg=Config.BG_COLOR)
    timer_label.pack(pady=5)

    # variables for tracking results
    test_start_time, recorded_distances = None, []
    test_is_running = False

    # counts the timer down
    def update_timer():
        nonlocal time_remaining, test_is_running
        if not test_is_running:
            return
        if time_remaining > 0:
            time_remaining -= 1
            timer_label.config(text=f"Time: {time_remaining}")
            tracking_window.after(1000, update_timer)
        else:
            end_test(auto=True)

    # moves the target 
    def move_target():
        nonlocal target_center_x, target_center_y, target_velocity_x, target_velocity_y, test_is_running
        if not test_is_running:
            return

        # changes the targets position for later
        target_center_x += target_velocity_x
        target_center_y += target_velocity_y
        
        # allows the target to bounce off edges
        if target_center_x - target_radius <= 0 or target_center_x + target_radius >= canvas_width:
            target_velocity_x *= -1
        if target_center_y - target_radius <= 0 or target_center_y + target_radius >= canvas_height:
            target_velocity_y *= -1

        # wobble is added based on impairment level
        wobble_offset_x = random.randint(-target_wobble, target_wobble)
        wobble_offset_y = random.randint(-target_wobble, target_wobble)
        adjusted_radius = target_radius + random.randint(-target_wobble // 2, target_wobble // 2)

        # takes the new updated coords and wobbles, then moves the target
        canvas.coords(target_shape_id,
                      target_center_x - adjusted_radius + wobble_offset_x,
                      target_center_y - adjusted_radius + wobble_offset_y,
                      target_center_x + adjusted_radius + wobble_offset_x,
                      target_center_y + adjusted_radius + wobble_offset_y)
        
        # provides the next movement
        tracking_window.after(30, move_target)

    # tracks the mouse in correlation to the target
    def record_mouse_position(event):
        if test_start_time:

            # calculates distance from target center and records it
            distance_from_target = math.dist((event.x, event.y), (target_center_x, target_center_y))
            recorded_distances.append(distance_from_target)

    # allows the program to record the mouse motion
    canvas.bind("<Motion>", record_mouse_position)

    # countdown before start of test
    def start_countdown(seconds_remaining=3):
        canvas.delete("all")

        # displays the countdown
        if seconds_remaining >= 0:
            canvas.create_text(canvas_width / 2, canvas_height / 2, text=str(seconds_remaining), font=("Helvetica", 40))
            tracking_window.after(1000, lambda: start_countdown(seconds_remaining - 1))
        else:
            start_test()

    # starts the test 
    def start_test():
        nonlocal test_start_time, target_shape_id, test_is_running

        # clears the inner box and adds the target
        canvas.delete("all")
        target_shape_id = canvas.create_oval(target_center_x - target_radius, target_center_y - target_radius,
                                             target_center_x + target_radius, target_center_y + target_radius,
                                             fill="red", outline="")
        
        # sets the starting time and state
        test_start_time = time.time()
        test_is_running = True
        update_timer()
        move_target()

    # ends the test
    def end_test(auto=False):
        nonlocal test_is_running
        if not test_start_time:
            return
        
        # records the end time and computes results
        test_is_running = False
        total_time_elapsed = time.time() - test_start_time

        # computes average distance and accuracy score
        average_distance = sum(recorded_distances) / len(recorded_distances) if recorded_distances else 0
        accuracy_score = max(0, 100 - min(average_distance / 5, 100))

        # uploads the results
        upload_test(user_id, total_time_elapsed, accuracy_score, impairment_level)

        message_text = "Time up!" if auto else "Test ended."
        messagebox.showinfo(
            "Tracking Results",
            f"{message_text}\nTotal time: {total_time_elapsed:.1f}s\nAverage distance: {average_distance:.1f}px"
        )

        # shows learning popup before closing
        from frontend.learn_popup import show_learn_popup
        show_learn_popup(parent_window, "tracking")

        # closes test window after showing results
        tracking_window.destroy()

    # controls for the test, in this case just an end button
    tk.Button(
        tracking_window,
        text="End Test",
        bg=Config.PRIMARY_COLOR,
        fg="white",
        font=("Helvetica", 11, "bold"),
        relief="flat",
        command=end_test
    ).pack(pady=10)

    # provides instructions on how to do the test before it starts
    messagebox.showinfo("How to Play", "Keep the cursor inside the circle")
    tracking_window.lift()
    tracking_window.focus_force()
    start_countdown()
