from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.bio_logic import (
    characterize_protein,
    detect_sequence_type,
    extract_sequence,
    transcribe_to_mrna,
    translate_mrna,
)
from app.blast_lookup import uniprot_lookup

BASE_DIR = Path(__file__).resolve().parent
app = FastAPI(title="DNA and RNA Sequence Analyzer")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def _build_default_context() -> dict:
    return {
        "input_sequence": "",
        "sequence_source": "",
        "detected_type": "",
        "detection_explanation": "",
        "transcribed_mrna": "",
        "transcription_explanation": "",
        "translation_explanation": "",
        "codon_rows": [],
        "amino_rows": [],
        "protein_sequence": "",
        "protein_properties": None,
        "protein_hits": [],
        "protein_explanation": "",
        "error": "",
        "selected_strand": "coding",
    }


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context=_build_default_context(),
    )


@app.post("/analyze", response_class=HTMLResponse)
async def analyze(
    request: Request,
    sequence_text: str = Form(default=""),
    dna_strand_type: str = Form(default="coding"),
    sequence_file: UploadFile | None = File(default=None),
):
    context = _build_default_context()
    context["selected_strand"] = dna_strand_type

    file_content = ""
    if sequence_file and sequence_file.filename:
        raw_bytes = await sequence_file.read()
        file_content = raw_bytes.decode("utf-8", errors="ignore")

    raw_input = sequence_text if sequence_text.strip() else file_content
    source = "Text area" if sequence_text.strip() else ("Uploaded file" if file_content.strip() else "")

    cleaned_sequence = extract_sequence(raw_input)
    detection = detect_sequence_type(cleaned_sequence)

    context["input_sequence"] = cleaned_sequence
    context["sequence_source"] = source
    context["detected_type"] = detection.seq_type
    context["detection_explanation"] = detection.explanation

    if detection.seq_type == "Invalid":
        context["error"] = "Please provide a valid DNA or RNA sequence."
        return templates.TemplateResponse(request=request, name="index.html", context=context)

    try:
        mrna, transcription_explanation = transcribe_to_mrna(
            sequence=detection.cleaned_sequence,
            seq_type=detection.seq_type,
            dna_strand_type=dna_strand_type,
        )
    except ValueError as exc:
        context["error"] = str(exc)
        return templates.TemplateResponse(request=request, name="index.html", context=context)

    codon_rows, amino_rows, protein_sequence, translation_explanation = translate_mrna(mrna)
    protein_properties = characterize_protein(protein_sequence)
    protein_hits = uniprot_lookup(protein_sequence) if protein_sequence else []

    context["transcribed_mrna"] = mrna
    context["transcription_explanation"] = transcription_explanation
    context["translation_explanation"] = translation_explanation
    context["codon_rows"] = codon_rows
    context["amino_rows"] = amino_rows
    context["protein_sequence"] = protein_sequence
    context["protein_properties"] = protein_properties
    context["protein_hits"] = protein_hits
    context["protein_explanation"] = (
        "We searched UniProt with your predicted protein sequence to find known proteins with matching sequence patterns. "
        "The matches suggest likely protein identity, source organism, and biological role."
        if protein_hits
        else "No UniProt matches were returned right now. This can happen for short sequences or temporary network/API limits."
    )

    return templates.TemplateResponse(request=request, name="index.html", context=context)
