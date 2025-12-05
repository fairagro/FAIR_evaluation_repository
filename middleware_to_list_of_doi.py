import re
import tkinter as tk
from tkinter import filedialog
from pathlib import Path

DOI_REGEX = r"10\.\d{4,9}/[^\s\"\'<>]+"  # basic DOI capture

# define multiple trailing-cleanup regex patterns
TRAILING_CLEANUPS = [
    re.compile(r'[.,;)\n"\'\s]+$'),          # trailing punctuation/whitespace
    re.compile(r'\\n.*$', re.IGNORECASE),

]

def clean_doi(doi: str) -> str:
    for pattern in TRAILING_CLEANUPS:
        doi = pattern.sub('', doi)
    # handle duplicated prefix like 10.20387/10.20387/...
    parts = doi.split('/')
    if len(parts) > 2 and parts[0] == parts[1]:
        doi = '/'.join(parts[1:])
    return doi


def extract_dois_from_file(file_path: Path):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    found = re.findall(DOI_REGEX, content)

    seen = set()
    unique_dois = []
    for doi in found:
        doi = clean_doi(doi)
        if doi and doi not in seen:
            seen.add(doi)
            unique_dois.append(doi)
    return unique_dois


def main():
    root = tk.Tk()
    root.withdraw()
    file_paths = filedialog.askopenfilenames(title="Select file(s) to extract DOIs")
    if not file_paths:
        print("No files selected")
        return

    for file_path in file_paths:
        path = Path(file_path)
        dois = extract_dois_from_file(path)
        print(f"\nFile: {file_path}")
        for doi in dois:
            print(doi)

        output_folder = path.parent / "output"
        output_folder.mkdir(exist_ok=True)
        output_file = output_folder / f"{path.stem}.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            for doi in dois:
                f.write(doi + "\n")
        print(f"Saved {len(dois)} unique DOIs to {output_file}")


if __name__ == "__main__":
    main()
