from rdflib import Graph
from pathlib import Path

def ttl_to_jsonld(folder: str) -> None:
    folder_path = Path(folder)
    output_folder = folder_path / "json"
    output_folder.mkdir(exist_ok=True)

    for ttl_file in folder_path.glob("*.ttl"):
        g = Graph()
        g.parse(ttl_file, format="turtle")

        output_file = output_folder / f"{ttl_file.stem}.jsonld"
        g.serialize(destination=output_file, format="json-ld")

if __name__ == "__main__":
    ttl_to_jsonld(r"H:\GitHub\FAIR_evaluation_repository\output\BonaRes")
