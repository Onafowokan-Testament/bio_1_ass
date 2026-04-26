import shutil
import uuid
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.core.calculator import MICROSCOPE_FACTORS, UNIT_TO_MM
from app.db.database import clear_records, delete_record, init_db, list_records
from app.services.records_service import run_and_save_calculation

BASE_DIR = Path(__file__).resolve().parent.parent
WEB_DIR = BASE_DIR / "phase_d_web"
UPLOADS_DIR = BASE_DIR / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)

app = FastAPI(title="Microscope Specimen Size Calculator")
app.mount("/static", StaticFiles(directory=WEB_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(WEB_DIR / "templates"))


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "microscopes": list(MICROSCOPE_FACTORS.keys()),
            "units": list(UNIT_TO_MM.keys()),
            "result": None,
            "error": None,
        },
    )


@app.post("/calculate")
async def calculate(
    request: Request,
    username: str = Form(...),
    measured_size_mm: str = Form(...),
    microscope_type: str = Form(...),
    output_unit: str = Form(...),
    specimen_image: UploadFile = File(...),
):
    if not specimen_image.filename:
        raise HTTPException(status_code=400, detail="Image file is required.")

    ext = Path(specimen_image.filename).suffix.lower()
    if ext not in {".png", ".jpg", ".jpeg", ".bmp", ".gif"}:
        raise HTTPException(status_code=400, detail="Invalid image format.")

    safe_name = f"{uuid.uuid4().hex}{ext}"
    image_path = UPLOADS_DIR / safe_name

    with image_path.open("wb") as out_file:
        shutil.copyfileobj(specimen_image.file, out_file)

    try:
        result = run_and_save_calculation(
            username=username,
            specimen_size_text=measured_size_mm,
            microscope_type=microscope_type,
            output_unit=output_unit,
            image_path=str(image_path),
        )
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "microscopes": list(MICROSCOPE_FACTORS.keys()),
                "units": list(UNIT_TO_MM.keys()),
                "result": result,
                "error": None,
            },
        )
    except ValueError as err:
        if image_path.exists():
            image_path.unlink()
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "microscopes": list(MICROSCOPE_FACTORS.keys()),
                "units": list(UNIT_TO_MM.keys()),
                "result": None,
                "error": str(err),
            },
        )


@app.get("/history")
def history(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="history.html",
        context={"records": list_records()},
    )


@app.post("/history/delete/{record_id}")
def history_delete(record_id: int):
    delete_record(record_id)
    return RedirectResponse(url="/history", status_code=303)


@app.post("/history/clear")
def history_clear():
    clear_records()
    return RedirectResponse(url="/history", status_code=303)
