# Microscope Specimen Size Calculator

This project implements all assignment phases using shared scientific logic and data persistence.

## Technology Used

- Python core modules for calculation and validation
- SQLite for database storage
- Tkinter for Phase (c) Python GUI
- FastAPI + Jinja2 templates + HTML/CSS for Phase (d) web GUI

## Project Structure

- app/core: Formula, microscope mapping, unit conversion, validation
- app/db: SQLite initialization and CRUD operations
- app/services: Shared orchestration for run-and-save flow
- phase_a_cli: Command-line interface for phases (a) and (b)
- phase_c_tkinter: Python GUI implementation for phase (c)
- phase_d_web: Web GUI implementation for phase (d)
- uploads: Stored uploaded images
- specimen_records.db: SQLite database file (auto-created)

## Core Formula

Real Size = Measured Size (mm) / Magnification Factor

Supported output units:

- nm
- um
- mm
- cm
- m

## Setup

1. Create virtual environment:

   python -m venv .venv

2. Activate virtual environment on PowerShell:

   .venv\Scripts\Activate.ps1

3. Install dependencies:

   pip install -r requirements.txt

## Run Phase (a) and (b) CLI

python -m phase_a_cli.main

## Run Phase (c) Tkinter GUI

python -m phase_c_tkinter.main

## Run Phase (d) FastAPI Web GUI

uvicorn phase_d_web.main:app --reload

Then open:

http://127.0.0.1:8000

## Hosting (Phase e)

Recommended free host: Render

1. Push project to GitHub
2. Create a new Web Service on Render
3. Build command:

   pip install -r requirements.txt

4. Start command:

   uvicorn phase_d_web.main:app --host 0.0.0.0 --port $PORT

If persistent storage is required after restarts, move from local SQLite file to a managed database.
