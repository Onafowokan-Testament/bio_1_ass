# Project 2: DNA & RNA Sequence Analyzer

Web-based application for CSC 442 Project 2.

## Features Implemented

- Three input methods:
  - type/paste in text area
  - upload file (.txt/.fasta)
  - drag-and-drop file
- Automatic DNA/RNA/Invalid detection with plain-English explanation
- DNA strand type option (coding or template) used in transcription
- Transcription output with explanation
- Translation with codon-to-amino-acid table and explanation
- Amino-acid chain with full name + abbreviations
- Protein characterization (length, molecular weight, hydrophobic ratio, acidic/basic counts)
- External lookup using UniProt with match display

## Run Locally

1. Create and activate virtual environment (PowerShell):

   python -m venv .venv
   .venv\Scripts\Activate.ps1

2. Install requirements:

   pip install -r requirements.txt

3. Run web app:

   uvicorn app.main:app --reload

4. Open browser:

   http://127.0.0.1:8000

## Deploy to Render

Build command:

pip install -r requirements.txt

Start command:

uvicorn app.main:app --host 0.0.0.0 --port $PORT
