from app.core.calculator import MICROSCOPE_FACTORS, UNIT_TO_MM
from app.db.database import clear_records, init_db, list_records
from app.services.records_service import run_and_save_calculation


def choose_from_list(title: str, options: list[str]) -> str:
    print(f"\n{title}")
    for idx, option in enumerate(options, start=1):
        print(f"{idx}. {option}")

    while True:
        choice = input("Select option number: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return options[int(choice) - 1]
        print("Invalid choice. Try again.")


def show_records() -> None:
    records = list_records()
    if not records:
        print("\nNo records found.")
        return

    print("\nSaved Records")
    print("-" * 100)
    for row in records:
        print(
            f"ID: {row['id']} | User: {row['username']} | Measured(mm): {row['specimen_size_mm']:.6f} "
            f"| Real(mm): {row['actual_size_mm']:.10f} | Real({row['output_unit']}): {row['actual_size_output']:.10f} "
            f"| Microscope: {row['microscope_type']} | Image: {row['image_path']} | Time: {row['created_at']}"
        )


def run_calculation_flow() -> None:
    username = input("Enter username: ").strip()
    image_path = input("Enter specimen image file path: ").strip()
    measured_text = input("Enter measured specimen size in mm: ").strip()

    microscope_type = choose_from_list(
        "Choose microscope type:", list(MICROSCOPE_FACTORS.keys())
    )
    output_unit = choose_from_list("Choose output unit:", list(UNIT_TO_MM.keys()))

    result = run_and_save_calculation(
        username=username,
        specimen_size_text=measured_text,
        microscope_type=microscope_type,
        output_unit=output_unit,
        image_path=image_path,
    )

    print("\nCalculation Result")
    print("-" * 50)
    print(f"Real size: {result.real_size_output:.10f} {result.output_unit}")
    print("\nBreakdown:")
    print(result.breakdown)


def main() -> None:
    init_db()

    while True:
        print("\nMicroscope Specimen Size Calculator")
        print("1. New calculation")
        print("2. View records")
        print("3. Clear records")
        print("4. Exit")

        option = input("Choose action: ").strip()
        try:
            if option == "1":
                run_calculation_flow()
            elif option == "2":
                show_records()
            elif option == "3":
                clear_records()
                print("All records deleted.")
            elif option == "4":
                print("Goodbye.")
                break
            else:
                print("Invalid option.")
        except ValueError as err:
            print(f"Error: {err}")


if __name__ == "__main__":
    main()
