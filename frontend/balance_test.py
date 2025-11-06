import tkinter as tk
from tkinter import messagebox
import random, math, time
from frontend.api_client import upload_test
from app.config import Config


def run_balance_game(root, user_id, mode="normal"):
    win = tk.Toplevel(root)
    win.title(f"Balance Game ({mode.capitalize()})")
    win.configure(bg=Config.BG_COLOR)
    win.focus_set()

    W, H = 600, 400
    canvas = tk.Canvas(win, width=W, height=H, bg="white")
    canvas.pack()

    # --- Mode settings ---
    levels = {
        "normal": {"gravity": 0.2, "tap_power": 5},
        "mild": {"gravity": 0.4, "tap_power": 4},
        "moderate": {"gravity": 0.6, "tap_power": 3},
        "severe": {"gravity": 0.8, "tap_power": 2},
    }
    gravity, tap_power = levels.get(mode, levels["normal"]).values()

    # --- Game state ---
    angle, score, running = 0, 0, True
    fail_limit = 70
    time_left = Config.BALANCE_TEST_DURATION

    # --- UI ---
    timer_label = tk.Label(
        win,
        text=f"Time: {time_left}",
        font=("Helvetica", 12, "bold"),
        fg=Config.PRIMARY_COLOR,
        bg=Config.BG_COLOR
    )
    timer_label.pack(pady=5)

    canvas.create_line(W/2, H/2-70, W/2, H/2+70, width=3, fill="#ccc")
    bar_length = 120
    bar = canvas.create_line(W/2, H/2, W/2, H/2 - bar_length, width=10, fill="blue")

    # --- Draw bar ---
    def draw_bar():
        x1, y1 = W/2, H/2
        x2 = x1 + bar_length * math.sin(math.radians(angle))
        y2 = y1 - bar_length * math.cos(math.radians(angle))
        canvas.coords(bar, x1, y1, x2, y2)
        tilt = abs(angle) / fail_limit
        color = "blue" if tilt < 0.5 else ("orange" if tilt < 0.8 else "red")
        canvas.itemconfig(bar, fill=color)

    # --- Gravity sway ---
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
        win.after(50, sway)

    # --- Player input ---
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

    # --- Fail ---
    def fail_game():
        nonlocal running
        if not running:
            return
        running = False
        messagebox.showwarning("You Fell!", "You lost your balance!")
        # Stop timer updates by setting running=False

    # --- End normally ---
    def end_game():
        nonlocal running
        if not running:
            return
        running = False
        accuracy = score / 500
        upload_test(user_id, Config.BALANCE_TEST_DURATION, accuracy, mode)
        messagebox.showinfo("Balance Results", f"Balance accuracy: {accuracy:.1f}")
        from frontend.learn_popup import show_learn_popup
        show_learn_popup(root, "balance")
        win.destroy()

    # --- Reset game ---
    def reset_game():
        win.destroy()
        run_balance_game(root, user_id, mode)

    # --- Controls ---
    button_frame = tk.Frame(win, bg=Config.BG_COLOR)
    button_frame.pack(pady=10)
    tk.Button(button_frame, text="Reset", command=reset_game,
              bg="#6c757d", fg="white", relief="flat", width=10).pack(side="left", padx=5)
    tk.Button(button_frame, text="End Test", command=end_game,
              bg=Config.PRIMARY_COLOR, fg="white", relief="flat", width=10).pack(side="left", padx=5)

    # --- Timer ---
    def update_timer():
        nonlocal time_left, running
        if not running:
            return
        if time_left > 0:
            time_left -= 1
            timer_label.config(text=f"Time: {time_left}")
            win.after(1000, update_timer)
        else:
            end_game()

    # --- Start game ---
    win.bind("<KeyPress>", on_press)
    draw_bar()
    sway()
    update_timer()
