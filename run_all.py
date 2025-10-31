import subprocess
import sys
import time
import requests
import os

def wait_for_server(url="http://127.0.0.1:5000", timeout=15):
    """Wait until Flask backend responds."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(url)
            if r.status_code in (200, 404):
                return True
        except requests.exceptions.ConnectionError:
            time.sleep(0.5)
    return False

def run_all():
    base = os.path.dirname(os.path.abspath(__file__))

    # Start Flask backend
    backend = subprocess.Popen(
        [sys.executable, "run_server.py"],
        cwd=base,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Wait until backend responds
    print("Starting backend...")
    if not wait_for_server():
        print("Backend did not start in time. Exiting.")
        backend.terminate()
        return
    print("Backend ready.")

    # Start frontend GUI
    try:
        subprocess.run([sys.executable, "-m", "frontend.main"], cwd=base)
    finally:
        backend.terminate()
        backend.wait(timeout=3)

if __name__ == "__main__":
    run_all()
