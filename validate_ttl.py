import tkinter as tk
from tkinter import filedialog
from pathlib import Path

TOOLS = {
    "fc": "fairagro:fc_measurement",
    "fes": "fairagro:fes_measurement",
    "fuji": "fairagro:fuji_measurement"
}

def main():
    root = tk.Tk()
    root.withdraw()
    file_paths = filedialog.askopenfilenames(title="Select file(s) to validate")
    if not file_paths:
        print("No files selected")
        return

    failed_files = []

    for file_path in file_paths:
        path = Path(file_path)
        if not path.is_file():
            print(f"File not found: {file_path}")
            continue

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        missing_tools = [tool for tool, prefix in TOOLS.items() if prefix not in content]

        if missing_tools:
            failed_files.append((file_path, missing_tools))
        else:
            print(f"All tools present in: {file_path}")

    if failed_files:
        print("\n=== Summary of files missing tools ===")
        for file_path, missing_tools in failed_files:
            print(f"{file_path}: missing {', '.join(missing_tools)}")
    else:
        print("\nAll files have all tools present!")

if __name__ == "__main__":
    main()
