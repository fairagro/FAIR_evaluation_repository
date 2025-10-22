import requests
import json

def fetch_identifiers(url: str) -> list[str]:
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    docs = data["response"]["docs"]
    dois: list[str] = []
    for doc in docs:
        ids = doc.get("mods.identifier", [])
        for identifier in ids:
            if identifier.startswith("10."):
                dois.append(identifier)
    return dois

def write_to_file(dois: list[str], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for doi in dois:
            f.write(doi + "\n")

if __name__ == "__main__":
    url = (
        "https://www.openagrar.de/servlets/solr/select?"
        "core=main&q=category.top%3A%22mir_genres%3Aresearch_data%22+"
        "AND+objectType%3Amods+AND+category.top%3A%22state%3Apublished%22"
        "&rows=300&fl=id%2Cmods.identifier&wt=json"
    )
    dois = fetch_identifiers(url)
    write_to_file(dois, "dois_list.txt")
    print(f"Wrote {len(dois)} DOIs to dois_list.txt")
