import tkinter as tk
from frontend.fitts_test import run_fitts_test
from frontend.quiz import run_quiz
from frontend.api_client import register_user
from app.config import Config


def main():
    root = tk.Tk()
    root.title("Inebriation Learning Tool")

    # --- main window sizing ---
    W, H = 600, 400
    root.geometry(f"{W}x{H}")
    root.minsize(W, H)

    # --- layout ---
    tk.Label(root, text="In-Ebriation Learning Tool", font=("Helvetica", 18, "bold")).pack(pady=20)
    tk.Label(root, text="Enter username to begin:", font=("Helvetica", 12)).pack()

    entry = tk.Entry(root, font=("Helvetica", 12))
    entry.pack(pady=10)

    def start_session():
        username = entry.get().strip()
        if not username:
            tk.messagebox.showwarning("Missing name", "Please enter a username.")
            return
        user_id = register_user(username)

        # Clear start widgets and show buttons
        for w in root.winfo_children():
            w.destroy()

        tk.Label(root, text=f"Welcome, {username}!", font=("Helvetica", 16, "bold")).pack(pady=20)
        tk.Button(root, text="Fitts' Law Test (Normal)",
                  command=lambda: run_fitts_test(root, user_id, mode="normal"),
                  width=25, height=2).pack(pady=5)

        tk.Button(root, text="Fitts' Law Test (Simulated)",
                  command=lambda: run_fitts_test(root, user_id, mode="simulated"),
                  width=25, height=2).pack(pady=5)

        tk.Button(root, text="Alcohol Knowledge Quiz",
                  command=lambda: run_quiz(root, user_id),
                  width=25, height=2).pack(pady=5)

        tk.Button(root, text="Exit", command=root.destroy, width=25, height=2).pack(pady=20)

    tk.Button(root, text="Start", command=start_session, font=("Helvetica", 12), width=15, height=1).pack(pady=10)

    root.mainloop()


if __name__ == "__main__":
    main()
