from __future__ import annotations

import re
import tkinter as tk
from tkinter import filedialog
from urllib.parse import unquote

import requests
from rdflib import Graph, Namespace


DCAT = Namespace("http://www.w3.org/ns/dcat#")
DOI_REGEX = re.compile(r"(10\.\d{4,9}/[^\s<>\"']+)", re.IGNORECASE)


def select_ttl_files() -> list[str]:
    root = tk.Tk()
    root.withdraw()
    return list(
        filedialog.askopenfilenames(
            title="Select TTL files",
            filetypes=[("Turtle files", "*.ttl")],
        )
    )


def extract_dois_from_ttl(path: str) -> set[str]:
    g = Graph()
    g.parse(path, format="turtle")

    dois: set[str] = set()

    for _, _, access_url in g.triples((None, DCAT.accessURL, None)):
        decoded = unquote(str(access_url))
        match = DOI_REGEX.search(decoded)
        if match:
            dois.add(match.group(1).lower())

    return dois


def best_date_from_crossref(doi: str) -> str:
    try:
        r = requests.get(
            f"https://api.crossref.org/works/{doi}",
            timeout=10,
        )
        if r.status_code != 200:
            return "unknown"

        msg = r.json().get("message", {})

        for field in ("published-online", "published-print", "issued"):
            parts = msg.get(field, {}).get("date-parts")
            if parts and parts[0]:
                return "-".join(str(x) for x in parts[0])

    except Exception:
        pass

    return "unknown"


def main() -> None:
    files = select_ttl_files()
    if not files:
        return

    all_dois: set[str] = set()
    for path in files:
        all_dois.update(extract_dois_from_ttl(path))

    for doi in sorted(all_dois):
        print(f"{doi}\t{best_date_from_crossref(doi)}")


if __name__ == "__main__":
    main()
