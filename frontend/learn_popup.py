import tkinter as tk

def show_learn_popup(parent, test_name):
    """Displays an educational message explaining alcohol's effects on the tested skill."""
    learn_window = tk.Toplevel(parent)
    learn_window.title("Learn More")
    learn_window.geometry("500x300")
    learn_window.transient(parent)
    learn_window.grab_set()

    learn_texts = {
        "fitts": (
            "Fitts' Law measures how quickly and accurately you can move toward a target.\n\n"
            "Alcohol slows reaction time and reduces motor control. "
            "This means it takes longer to aim and click accurately — "
            "the same effect that makes fine hand movements, like steering or texting, less precise after drinking."
        ),
        "tracking": (
            "The Target Tracking Test measures your ability to maintain focus and smooth motor movement.\n\n"
            "Alcohol impairs your eye-hand coordination and predictive tracking — "
            "causing over- or under-corrections, similar to drifting in a driving lane or missing moving objects."
        ),
        "balance": (
            "The Balance Game tests stability and control — functions of your cerebellum.\n\n"
            "Alcohol disrupts the cerebellum’s signaling, causing sway, delayed correction, and loss of equilibrium. "
            "Even small doses can increase fall risk or reduce postural stability."
        ),
        "typing": (
            "The Typing Test measures fine motor precision and cognitive focus.\n\n"
            "Alcohol decreases both. Neural communication slows, finger accuracy drops, "
            "and error recognition becomes delayed — much like texting errors that increase after drinking."
        ),
    }

    text = learn_texts.get(test_name, "This test demonstrates how alcohol impairs reaction time and coordination.")
    tk.Label(learn_window, text="Learn More", font=("Helvetica", 16, "bold")).pack(pady=10)
    msg = tk.Message(learn_window, text=text, width=460, font=("Helvetica", 11))
    msg.pack(pady=10)
    tk.Button(learn_window, text="Close", command=learn_window.destroy).pack(pady=10)
