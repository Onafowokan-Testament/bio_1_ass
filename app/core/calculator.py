from dataclasses import dataclass
from typing import Dict

MICROSCOPE_FACTORS: Dict[str, float] = {
    "Compound Light Microscope (40x)": 40.0,
    "Compound Light Microscope (100x)": 100.0,
    "Compound Light Microscope (400x)": 400.0,
    "Stereo Microscope (20x)": 20.0,
    "Electron Microscope (10000x)": 10000.0,
}

UNIT_TO_MM: Dict[str, float] = {
    "nm": 1e-6,
    "um": 1e-3,
    "mm": 1.0,
    "cm": 10.0,
    "m": 1000.0,
}


@dataclass
class CalculationResult:
    username: str
    measured_size_mm: float
    microscope_type: str
    magnification_factor: float
    real_size_mm: float
    output_unit: str
    real_size_output: float
    breakdown: str


def validate_username(username: str) -> str:
    cleaned = (username or "").strip()
    if not cleaned:
        raise ValueError("Username is required.")
    return cleaned


def validate_measured_size(size_text: str) -> float:
    try:
        value = float(size_text)
    except (TypeError, ValueError) as exc:
        raise ValueError("Measured size must be a valid number.") from exc

    if value <= 0:
        raise ValueError("Measured size must be greater than 0.")
    return value


def convert_mm_to_unit(value_mm: float, output_unit: str) -> float:
    if output_unit not in UNIT_TO_MM:
        raise ValueError(f"Unsupported output unit: {output_unit}")
    return value_mm / UNIT_TO_MM[output_unit]


def calculate_real_size(
    username: str,
    measured_size_mm: float,
    microscope_type: str,
    output_unit: str,
) -> CalculationResult:
    cleaned_username = validate_username(username)

    if measured_size_mm <= 0:
        raise ValueError("Measured size must be greater than 0.")

    if microscope_type not in MICROSCOPE_FACTORS:
        raise ValueError("Invalid microscope type selected.")

    if output_unit not in UNIT_TO_MM:
        raise ValueError("Invalid output unit selected.")

    magnification_factor = MICROSCOPE_FACTORS[microscope_type]
    real_size_mm = measured_size_mm / magnification_factor
    real_size_output = convert_mm_to_unit(real_size_mm, output_unit)

    breakdown = (
        "Real Size = Measured Size / Magnification\n"
        f"Measured Size = {measured_size_mm:.6f} mm\n"
        f"Magnification = {magnification_factor:g}x\n"
        f"Real Size (mm) = {measured_size_mm:.6f} / {magnification_factor:g} = {real_size_mm:.10f} mm\n"
        f"Converted to {output_unit}: {real_size_output:.10f} {output_unit}"
    )

    return CalculationResult(
        username=cleaned_username,
        measured_size_mm=measured_size_mm,
        microscope_type=microscope_type,
        magnification_factor=magnification_factor,
        real_size_mm=real_size_mm,
        output_unit=output_unit,
        real_size_output=real_size_output,
        breakdown=breakdown,
    )
