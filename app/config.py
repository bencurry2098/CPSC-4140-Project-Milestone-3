import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # backend
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # frontend
    CANVAS_WIDTH = 900
    CANVAS_HEIGHT = 750
    MIN_TARGET_RADIUS = 20
    MAX_TARGET_RADIUS = 50

    # timer durations (seconds)
    TRACKING_TEST_DURATION = 10
    BALANCE_TEST_DURATION = 15

    # UI theme
    BG_COLOR = "#f8f9fa"
    PRIMARY_COLOR = "#1f77b4"
    ACCENT_COLOR = "#d9534f"
    FONT_TITLE = ("Helvetica", 22, "bold")
    FONT_SUBTITLE = ("Helvetica", 20, "bold")
    FONT_BODY = ("Helvetica", 16)
