import tkinter as tk
from tkinter import messagebox
import random, math, time, csv, os
from frontend.api_client import upload_test
from app.config import Config
from PIL import Image, ImageTk, ImageDraw

def run_balance_game(root, user_id, mode="normal"):
    win = tk.Toplevel(root)
    win.title(f"Balance Game ({mode.capitalize()})")
    W, H = 600, 400
    canvas = tk.Canvas(win, width=W, height=H, bg="white")
    canvas.pack()

    levels = {
        "normal": {"sway": 0.5, "delay": 0},
        "mild": {"sway": 1.0, "delay": 100},
        "moderate": {"sway": 2.0, "delay": 200},
        "severe": {"sway": 3.0, "delay": 400},
    }
    sway_strength, delay = levels.get(mode, levels["normal"]).values()

    line = canvas.create_line(W/2, H/2-50, W/2, H/2+50, width=8, fill="blue")
    angle, score, running = 0, 0, True

    def sway():
        nonlocal angle, score
        if not running: return
        angle += random.uniform(-sway_strength, sway_strength)
        angle = max(-45, min(45, angle))
        draw_bar()
        score += max(0, 45 - abs(angle))
        win.after(100, sway)

    def draw_bar():
        x1, y1 = W/2, H/2
        x2 = x1 + 100 * math.sin(math.radians(angle))
        y2 = y1 + 100 * math.cos(math.radians(angle))
        canvas.coords(line, x1, y1, x2, y2)

    def key_press(event):
        nonlocal angle
        if delay:
            win.after(delay, lambda: adjust(event))
        else:
            adjust(event)

    def adjust(event):
        nonlocal angle
        if event.keysym == "Left": angle -= 2
        elif event.keysym == "Right": angle += 2

    def end_game():
        nonlocal running
        running = False
        accuracy = score / 100
        messagebox.showinfo("Result", f"Balance score: {accuracy:.1f}")
        win.destroy()

    win.bind("<KeyPress>", key_press)
    sway()
    win.after(10000, end_game)
