import tkinter as tk
from app.config import Config


def show_learn_popup(root, test_type, mode="normal"):
    # Educational popup after each test with consistent styling.
    popup = tk.Toplevel(root)
    popup.title("Learn More")
    popup.configure(bg=Config.BG_COLOR)
    popup.geometry("500x350")
    popup.transient(root)
    popup.grab_set()

    # Titles
    tk.Label(
        popup,
        text="Understanding Your Results",
        font=Config.FONT_SUBTITLE,
        bg=Config.BG_COLOR,
        fg=Config.PRIMARY_COLOR
    ).pack(pady=(20, 10))

    # Text body depending on test
    text_box = tk.Text(
        popup,
        wrap="word",
        bg=Config.BG_COLOR,
        fg="black",
        font=Config.FONT_BODY,
        relief="flat",
        height=10,
        width=60,
        padx=20,
        pady=5
    )
    
    # Insert educational content
    text_box.pack(padx=10, pady=(0, 15))
    text_box.insert("1.0", get_learn_text(test_type, mode))
    # Disable editing
    text_box.config(state="disabled")

    # Close button
    tk.Button(
        popup,
        text="Close",
        command=popup.destroy,
        bg=Config.PRIMARY_COLOR,
        fg="white",
        font=("Helvetica", 11, "bold"),
        relief="flat",
        width=12
    ).pack(pady=10)
    popup.update_idletasks()
    center_window(popup, root)


def get_learn_text(test_type, mode="normal"):
    # Return educational content for each test and impairment level.
    if test_type == "fitts":
        if mode == "normal":
            return (
                "In the normal condition, there are no simulated impairments. "
                "Your movements reflect baseline coordination, allowing accurate "
                "and quick targeting without delay or instability."
            )

        elif mode == "mild":
            return (
                "The mild impairment introduces a slight delay and hand jitter, "
                "mimicking how low levels of alcohol cause slowed reaction time "
                "and minor tremors. Users often experience reduced precision and "
                "slower corrective motion, similar to early-stage intoxication."
            )

        elif mode == "moderate":
            return (
                "The moderate impairment adds more jitter and occasional reversed movements. "
                "This models mid-level intoxication, where alcohol begins to disrupt "
                "the brain’s coordination pathways and spatial perception. "
                "Reaching accurately becomes inconsistent, and overcorrection increases."
            )

        elif mode == "severe":
            return (
                "The severe condition introduces visual ghosting, motion sway, and heavy input delay. "
                "This reflects high-level intoxication where perception, reaction, and fine motor control "
                "are all impaired. Visual double images and delayed responses make accurate targeting "
                "extremely difficult, similar to late-stage inebriation."
            )

        # fallback for unexpected mode
        return (
            "Fitts’ Law describes how movement time depends on target size and distance. "
            "Alcohol slows both reaction time and precision, causing longer response durations "
            "as impairment severity increases."
        )

    elif test_type == "tracking":
        return (
            "The Target Tracking Test simulates the coordination needed to follow moving objects, "
            "similar to maintaining lane position while driving. Alcohol increases involuntary "
            "hand movement and reduces spatial accuracy, which causes greater average distance "
            "from the moving target in this simulation."
        )

    elif test_type == "balance":
        return (
            "The Balance Game models how alcohol disrupts the inner ear and motor response systems. "
            "Even small amounts of alcohol affect postural control, making it harder to maintain balance "
            "or make fine corrections. This demonstrates how quickly coordination can degrade under influence."
        )

    elif test_type == "typing":
        return (
            "The Typing Test shows how alcohol affects reflexes and precision. Increased error rates "
            "and slower reaction times mirror the impaired ability to type or interact accurately "
            "with digital interfaces after drinking."
        )

    elif test_type == "quiz":
        return (
            "The Knowledge Quiz reinforces understanding of alcohol’s effects on motor skills, "
            "reaction time, and judgment. Learning how these impairments occur helps users recognize "
            "why responsible choices and awareness are crucial for safety."
        )

    return (
        "This test demonstrates how alcohol impairs different cognitive and motor functions. "
        "Use the results to reflect on how reaction time, balance, and precision can all be affected."
    )


def center_window(window, parent):
    # Center popup relative to parent window.
    window.update_idletasks()
    px = parent.winfo_x()
    py = parent.winfo_y()
    pw = parent.winfo_width()
    ph = parent.winfo_height()
    ww = window.winfo_width()
    wh = window.winfo_height()
    x = px + (pw - ww) // 2
    y = py + (ph - wh) // 2
    window.geometry(f"+{x}+{y}")
