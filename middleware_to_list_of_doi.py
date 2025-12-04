import json
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
import re

def main(numbered: bool = False, write_output: bool = False):
    def read_dois(file_path: str):
        path = Path(file_path)
        if not path.is_file():
            print(f"File not found: {file_path}")
            return []

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        doi_pattern = re.compile(r"(10\.\d{4,9}/[-._;()/:A-Z0-9]+)", re.IGNORECASE)
        dois = []

        def extract_from_obj(obj):
            if isinstance(obj, dict):
                for value in obj.values():
                    extract_from_obj(value)
            elif isinstance(obj, list):
                for item in obj:
                    extract_from_obj(item)
            elif isinstance(obj, str):
                matches = doi_pattern.findall(obj)
                for match in matches:
                    cleaned = match.rstrip(").; ")
                    dois.append(cleaned)

        extract_from_obj(data)
        return dois

    root = tk.Tk()
    root.withdraw()
    file_paths = filedialog.askopenfilenames(
        title="Select JSON file(s)",
        filetypes=[("JSON files", "*.json")]
    )

    if not file_paths:
        print("No file selected")
        return

    for file_path in file_paths:
        print(f"\nProcessing: {file_path}")
        dois = read_dois(file_path)
        for i, doi in enumerate(dois, start=1):
            if numbered:
                print(f"{i}. {doi}")
            else:
                print(doi)

        if write_output:
            input_path = Path(file_path)
            output_dir = input_path.parent / "output"
            output_dir.mkdir(exist_ok=True)
            output_path = output_dir / f"{input_path.stem}.txt"

            with open(output_path, "w", encoding="utf-8") as f:
                for doi in dois:
                    f.write(f"{doi}\n")
            print(f"Results written to {output_path}")


if __name__ == "__main__":
    main(numbered=True, write_output=True)
