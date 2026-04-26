import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from app.core.calculator import MICROSCOPE_FACTORS, UNIT_TO_MM
from app.db.database import clear_records, delete_record, init_db, list_records
from app.services.records_service import run_and_save_calculation


class SpecimenCalculatorApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Microscope Specimen Size Calculator - Tkinter GUI")
        self.root.geometry("1100x700")

        init_db()

        self.username_var = tk.StringVar()
        self.size_var = tk.StringVar()
        self.image_path_var = tk.StringVar()
        self.microscope_var = tk.StringVar(value=list(MICROSCOPE_FACTORS.keys())[0])
        self.unit_var = tk.StringVar(value=list(UNIT_TO_MM.keys())[0])

        self.preview_image = None

        self._build_layout()
        self.refresh_records()

    def _build_layout(self) -> None:
        container = ttk.Frame(self.root, padding=12)
        container.pack(fill=tk.BOTH, expand=True)

        form = ttk.LabelFrame(container, text="Calculation Input", padding=10)
        form.pack(fill=tk.X)

        ttk.Label(form, text="Username:").grid(
            row=0, column=0, sticky="w", padx=6, pady=6
        )
        ttk.Entry(form, textvariable=self.username_var, width=30).grid(
            row=0, column=1, sticky="we", padx=6, pady=6
        )

        ttk.Label(form, text="Measured Size (mm):").grid(
            row=1, column=0, sticky="w", padx=6, pady=6
        )
        ttk.Entry(form, textvariable=self.size_var, width=30).grid(
            row=1, column=1, sticky="we", padx=6, pady=6
        )

        ttk.Label(form, text="Microscope Type:").grid(
            row=2, column=0, sticky="w", padx=6, pady=6
        )
        ttk.Combobox(
            form,
            textvariable=self.microscope_var,
            values=list(MICROSCOPE_FACTORS.keys()),
            state="readonly",
            width=42,
        ).grid(row=2, column=1, sticky="we", padx=6, pady=6)

        ttk.Label(form, text="Output Unit:").grid(
            row=3, column=0, sticky="w", padx=6, pady=6
        )
        ttk.Combobox(
            form,
            textvariable=self.unit_var,
            values=list(UNIT_TO_MM.keys()),
            state="readonly",
            width=42,
        ).grid(row=3, column=1, sticky="we", padx=6, pady=6)

        ttk.Label(form, text="Specimen Image:").grid(
            row=4, column=0, sticky="w", padx=6, pady=6
        )
        ttk.Entry(
            form, textvariable=self.image_path_var, width=48, state="readonly"
        ).grid(row=4, column=1, sticky="we", padx=6, pady=6)
        ttk.Button(form, text="Browse", command=self.select_image).grid(
            row=4, column=2, padx=6, pady=6
        )

        ttk.Button(form, text="Calculate & Save", command=self.calculate).grid(
            row=5, column=1, sticky="e", padx=6, pady=8
        )

        form.columnconfigure(1, weight=1)

        content = ttk.Frame(container)
        content.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        left = ttk.LabelFrame(content, text="Image Preview", padding=10)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        self.image_label = ttk.Label(left, text="No image selected")
        self.image_label.pack(fill=tk.BOTH, expand=True)

        right = ttk.LabelFrame(content, text="Result Breakdown", padding=10)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        self.result_text = tk.Text(right, height=16, wrap="word")
        self.result_text.pack(fill=tk.BOTH, expand=True)

        history_frame = ttk.LabelFrame(container, text="Saved Records", padding=10)
        history_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        columns = (
            "id",
            "username",
            "specimen_size_mm",
            "actual_size_output",
            "output_unit",
            "microscope_type",
            "image_path",
            "created_at",
        )

        self.tree = ttk.Treeview(
            history_frame, columns=columns, show="headings", height=10
        )
        for col in columns:
            self.tree.heading(col, text=col)

        self.tree.column("id", width=40, anchor="center")
        self.tree.column("username", width=100)
        self.tree.column("specimen_size_mm", width=110, anchor="e")
        self.tree.column("actual_size_output", width=130, anchor="e")
        self.tree.column("output_unit", width=80, anchor="center")
        self.tree.column("microscope_type", width=220)
        self.tree.column("image_path", width=220)
        self.tree.column("created_at", width=140)
        self.tree.pack(fill=tk.BOTH, expand=True)

        actions = ttk.Frame(history_frame)
        actions.pack(fill=tk.X, pady=(8, 0))
        ttk.Button(actions, text="Delete Selected", command=self.delete_selected).pack(
            side=tk.LEFT
        )
        ttk.Button(actions, text="Clear All", command=self.clear_all).pack(
            side=tk.LEFT, padx=(8, 0)
        )
        ttk.Button(actions, text="Refresh", command=self.refresh_records).pack(
            side=tk.LEFT, padx=(8, 0)
        )

    def select_image(self) -> None:
        file_path = filedialog.askopenfilename(
            title="Select specimen image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif")],
        )
        if not file_path:
            return
        self.image_path_var.set(file_path)
        self.show_preview(file_path)

    def show_preview(self, file_path: str) -> None:
        path = Path(file_path)
        if not path.exists():
            self.image_label.configure(text="Image not found", image="")
            return

        try:
            self.preview_image = tk.PhotoImage(file=str(path))
            self.image_label.configure(image=self.preview_image, text="")
        except tk.TclError:
            self.preview_image = None
            self.image_label.configure(
                image="",
                text="Preview unavailable for this format in Tkinter. PNG/GIF are supported.",
            )

    def calculate(self) -> None:
        try:
            result = run_and_save_calculation(
                username=self.username_var.get(),
                specimen_size_text=self.size_var.get(),
                microscope_type=self.microscope_var.get(),
                output_unit=self.unit_var.get(),
                image_path=self.image_path_var.get(),
            )
        except ValueError as err:
            messagebox.showerror("Error", str(err))
            return

        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(
            tk.END,
            f"Real size: {result.real_size_output:.10f} {result.output_unit}\n\n{result.breakdown}",
        )
        self.refresh_records()
        messagebox.showinfo("Success", "Calculation completed and saved.")

    def refresh_records(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in list_records():
            self.tree.insert(
                "",
                tk.END,
                values=(
                    row["id"],
                    row["username"],
                    f"{row['specimen_size_mm']:.6f}",
                    f"{row['actual_size_output']:.10f}",
                    row["output_unit"],
                    row["microscope_type"],
                    row["image_path"],
                    row["created_at"],
                ),
            )

    def delete_selected(self) -> None:
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a record first.")
            return

        item = self.tree.item(selected[0])
        record_id = int(item["values"][0])
        delete_record(record_id)
        self.refresh_records()

    def clear_all(self) -> None:
        if messagebox.askyesno("Confirm", "Delete all records?"):
            clear_records()
            self.refresh_records()


def main() -> None:
    root = tk.Tk()
    SpecimenCalculatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
