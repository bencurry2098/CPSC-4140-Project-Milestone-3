import tkinter as tk
from tkinter import messagebox
import random, math, time
from frontend.api_client import upload_test
from app.config import Config
from frontend.learn_popup import show_learn_popup

# runs the game and sets the default impairment level to be normal
def run_balance_game(root, user_id, mode="normal"):
    # create window for the game
    balance_window = tk.Toplevel(root)
    balance_window.title(f"Balance Game ({mode.capitalize()})")
    balance_window.configure(bg=Config.BG_COLOR)
    balance_window.focus_set()

    # setup inner box for game
    W, H = Config.CANVAS_WIDTH, Config.CANVAS_WIDTH
    canvas = tk.Canvas(balance_window, width=W, height=H, bg="white")
    canvas.pack()

    # impairment levels and effects
    levels = {
        "normal": {"gravity": 0.2, "tap_power": 5},
        "mild": {"gravity": 0.4, "tap_power": 4},
        "moderate": {"gravity": 0.6, "tap_power": 3},
        "severe": {"gravity": 0.8, "tap_power": 2},
    }
    gravity, tap_power = levels.get(mode, levels["normal"]).values()

    # setup the game
    angle, score, running = 0, 0, False
    fail_limit = 70
    time_left = Config.BALANCE_TEST_DURATION

    # create the timer
    timer_label = tk.Label(
        balance_window,
        text=f"Time: {time_left}",
        font=("Helvetica", 18, "bold"),
        fg=Config.PRIMARY_COLOR,
        bg=Config.BG_COLOR
    )
    timer_label.pack(pady=5)

    # initializes the reference line and the balance bar
    canvas.create_line(W/2, H/2-70, W/2, H/2+70, width=3, fill="#ccc")
    bar_length = 120
    bar = canvas.create_line(W/2, H/2, W/2, H/2 - bar_length, width=10, fill="blue")

    # redraws the bar based on the angle
    def draw_bar():
        x1, y1 = W/2, H/2
        x2 = x1 + bar_length * math.sin(math.radians(angle))
        y2 = y1 - bar_length * math.cos(math.radians(angle))
        canvas.coords(bar, x1, y1, x2, y2)
        tilt = abs(angle) / fail_limit
        color = "blue" if tilt < 0.5 else ("orange" if tilt < 0.8 else "red")
        canvas.itemconfig(bar, fill=color)

    # changes the angle that gets used to redraw the bar
    def sway():
        nonlocal angle, score, running
        if not running:
            return
        angle += gravity * (1 if angle > 0 else -1)
        angle = max(-90, min(90, angle))
        draw_bar()
        if abs(angle) >= fail_limit:
            fail_game()
            return
        score += max(0, fail_limit - abs(angle))
        balance_window.after(50, sway)

    # Makes it so that the left and right arrow keys can move the bar
    def on_press(event):
        nonlocal angle
        if not running:
            return
        if event.keysym == "Left":
            angle -= tap_power
        elif event.keysym == "Right":
            angle += tap_power
        angle = max(-90, min(90, angle))
        draw_bar()
        if abs(angle) >= fail_limit:
            fail_game()

    # If bar reaches a certain threshold the player fails
    def fail_game():
        nonlocal running
        if not running:
            return
        running = False
        messagebox.showwarning("You Fell!", "You lost your balance!")
        show_learn_popup(root, "balance")
        balance_window.destroy()

    # ends the game and opens the learning window
    def end_game():
        nonlocal running
        if not running:
            return
        running = False
        accuracy = score / 500
        upload_test(user_id, Config.BALANCE_TEST_DURATION, accuracy, mode)
        messagebox.showinfo("Balance Results", f"Balance accuracy: {accuracy:.1f}")
        show_learn_popup(root, "balance")
        balance_window.destroy()

    # restarts the game
    def reset_game():
        balance_window.destroy()
        run_balance_game(root, user_id, mode)

    # buttons for resetting and ending the game
    button_frame = tk.Frame(balance_window, bg=Config.BG_COLOR)
    button_frame.pack(pady=10)
    tk.Button(button_frame, text="Reset", command=reset_game,
              bg="#6c757d", fg="white", relief="flat", width=10).pack(side="left", padx=5)
    tk.Button(button_frame, text="End Test", command=end_game,
              bg=Config.PRIMARY_COLOR, fg="white", relief="flat", width=10).pack(side="left", padx=5)

    # counts the timer down
    def update_timer():
        nonlocal time_left, running
        if not running:
            return
        if time_left > 0:
            time_left -= 1
            timer_label.config(text=f"Time: {time_left}")
            balance_window.after(1000, update_timer)
        else:
            end_game()

    # start the game
    balance_window.bind("<KeyPress>", on_press)
    draw_bar()

    # give instructions to the user before the game starts
    messagebox.showinfo("How to Play", "Press the right and left arrow keys to balance the bar")
    balance_window.lift()
    balance_window.focus_force()
    running = True
    sway()
    update_timer()
