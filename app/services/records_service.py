from pathlib import Path

from app.core.calculator import calculate_real_size, validate_measured_size, validate_username
from app.db.database import insert_record


def run_and_save_calculation(
    username: str,
    specimen_size_text: str,
    microscope_type: str,
    output_unit: str,
    image_path: str,
):
    user = validate_username(username)
    specimen_size_mm = validate_measured_size(specimen_size_text)

    if not image_path:
        raise ValueError("Specimen image is required.")

    if not Path(image_path).exists():
        raise ValueError("Selected image file does not exist.")

    result = calculate_real_size(
        username=user,
        measured_size_mm=specimen_size_mm,
        microscope_type=microscope_type,
        output_unit=output_unit,
    )

    insert_record(
        username=result.username,
        image_path=image_path,
        specimen_size_mm=result.measured_size_mm,
        microscope_type=result.microscope_type,
        output_unit=result.output_unit,
        actual_size_mm=result.real_size_mm,
        actual_size_output=result.real_size_output,
    )

    return result
