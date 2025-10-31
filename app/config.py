import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # --- backend settings ---
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- shared frontend constants ---
    CANVAS_WIDTH = 800
    CANVAS_HEIGHT = 600
    MIN_TARGET_RADIUS = 20
    MAX_TARGET_RADIUS = 100
    NUM_TRIALS = 10
