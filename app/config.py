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
    MAX_TARGET_RADIUS = 100
    NUM_TRIALS = 10

    # --- timer durations (seconds) ---
    TRACKING_TEST_DURATION = 20
    FITTS_TEST_DURATION = 30
    BALANCE_TEST_DURATION = 15
