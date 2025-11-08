# Makefile for CPSC 4140 Milestone 3 Project

# Detect platform
ifeq ($(OS),Windows_NT)
	PYTHON := python
	PIP := venv\Scripts\pip
	PY := venv\Scripts\python
else
	PYTHON := python3
	PIP := venv/bin/pip
	PY := venv/bin/python
endif

# Directories and files
VENV := venv
DATA_DIR := data
APP_DIR := app
FRONT_DIR := frontend
REQ_FILE := requirements.txt
DB_FILE := $(APP_DIR)/database.db

# Default target
help:
	@echo "Available commands:"
	@echo "  make env          - Create venv and install dependencies"
	@echo "  make run          - Run both backend and frontend"
	@echo "  make backend      - Run Flask backend only"
	@echo "  make frontend     - Run Tkinter frontend only"
	@echo "  make clean        - Remove temporary and data files"
	@echo "  make reset-db     - Recreate SQLite database"

# Environment setup
env:
	@echo "Creating virtual environment..."
	$(PYTHON) -m venv $(VENV)
	@echo "Installing dependencies..."
	$(PIP) install --upgrade pip
	$(PIP) install -r $(REQ_FILE)
	@echo "Virtual environment created and dependencies installed."
	@echo "Activate manually with: source venv/bin/activate"

# Run tasks
run:
	@echo "Starting full system (backend + frontend)..."
	$(PY) run_all.py

backend:
	@echo "Starting Flask backend..."
	$(PY) run_server.py

frontend:
	@echo "Starting Tkinter frontend..."
	$(PY) -m $(FRONT_DIR).main

# Maintenance
clean:
	@echo "Cleaning up temporary files..."
	@rm -rf __pycache__ */__pycache__ *.pyc *.pyo
	@rm -rf $(DATA_DIR)/*.csv $(DATA_DIR)/*.png
	@rm -rf build dist *.egg-info
	@echo "Cleanup complete."

reset-db:
	@echo "Resetting database..."
	@rm -f $(DB_FILE)
	$(PY) -c "from app.routes import app; from app.models import db; app.app_context().push(); db.create_all(); print('Database recreated.')"
