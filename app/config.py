import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # --- backend settings ---
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- shared frontend constants ---
    CANVAS_WIDTH = 900
    CANVAS_HEIGHT = 750
    MIN_TARGET_RADIUS = 20
    MAX_TARGET_RADIUS = 50
    NUM_TRIALS = 10

    # --- timer durations (seconds) ---
    TRACKING_TEST_DURATION = 20
    FITTS_TEST_DURATION = 30
    BALANCE_TEST_DURATION = 15

    # --- UI theme ---
    BG_COLOR = "#f8f9fa"
    PRIMARY_COLOR = "#1f77b4"
    ACCENT_COLOR = "#d9534f"
    FONT_TITLE = ("Helvetica", 18, "bold")
    FONT_SUBTITLE = ("Helvetica", 14, "bold")
    FONT_BODY = ("Helvetica", 12)
