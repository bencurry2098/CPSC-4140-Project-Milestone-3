import requests

BASE_URL = "http://127.0.0.1:5000"

def register_user(username):
    try:
        r = requests.post(f"{BASE_URL}/register", json={"username": username})
        data = r.json()
        return data.get("user_id")
    except Exception:
        from tkinter import messagebox
        messagebox.showerror("Server Error", "Unable to contact backend. Is Flask running?")
        raise

def upload_test(user_id, avg_time, accuracy, mode):
    payload = {"user_id": user_id, "avg_time": avg_time, "accuracy": accuracy, "mode": mode}
    requests.post(f"{BASE_URL}/upload_test", json=payload)

def upload_quiz(user_id, score, total_questions):
    payload = {"user_id": user_id, "score": score, "total_questions": total_questions}
    requests.post(f"{BASE_URL}/upload_quiz", json=payload)
