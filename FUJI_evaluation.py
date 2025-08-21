import os
import json
from dotenv import load_dotenv
import requests
import csv
from typing import Dict, Any, Optional
from requests.exceptions import ConnectTimeout
from config import fuji_testing

# Load dotenv
load_dotenv()

USE_FUJI_AUTH = os.getenv("USE_FUJI_AUTH", "false").lower() == "true"
USERNAME = os.getenv("FUJI_USERNAME")
PASSWORD = os.getenv("FUJI_PASSWORD")

fuji_auth: Optional[tuple[str, str]] = (USERNAME, PASSWORD) if USE_FUJI_AUTH else None

if fuji_testing:
    FUJI_URL = os.getenv("FUJI_LOCAL")
else:
    FUJI_URL = os.getenv("FUJI_URL")
if not FUJI_URL:
    raise RuntimeError("FUJI_URL is not set in .env file")
headers = {
    'accept': '*/*',
    'Content-Type': 'application/json'
}

data_example = {
    "object_identifier": "DOI: 10.20387/bonares-zyd4-w9c2",
    "test_debug": True,
    "metadata_service_endpoint": "",
    "metadata_service_type": "oai_pmh",
    "use_datacite": True,
    "metric_version": "metrics_v0.5"
}

# Example FUJI evaluation results
fuji_evaluation_result_example = {
    'FsF-F1-01D-1': 1.0, 'FsF-F1-01D-2': 1.0, 'FsF-F1-02D-1': 1.0, 'FsF-F1-02D-2': 1.0,
    'FsF-F2-01M-1': 0.5, 'FsF-F2-01M-2': 0.5, 'FsF-F2-01M-3': 0.5, 'FsF-F3-01M-1': 0.0,
    'FsF-F3-01M-2': 0.0, 'FsF-F4-01M-1': 1.0, 'FsF-F4-01M-2': 1.0,
    'FsF-A1-01M-1': 0.0, 'FsF-A1-01M-2': 0.0, 'FsF-A1-01M-3': 0.0, 'FsF-A1-02M-1': 1.0,
    'FsF-A1-03D-1': 0.0, 'FsF-I1-01M-1': 0.5, 'FsF-I1-01M-2': 0.5, 'FsF-I2-01M-1': 0.0,
    'FsF-I2-01M-2': 0.0, 'FsF-I3-01M-1': 1.0, 'FsF-I3-01M-2': 1.0,
    'FsF-R1-01MD-1': 0.25, 'FsF-R1-01MD-1a': 0.25, 'FsF-R1-01MD-1b': 0.25,
    'FsF-R1-01MD-2': 0.25, 'FsF-R1-01MD-2a': 0.25, 'FsF-R1-01MD-2b': 0.25,
    'FsF-R1-01MD-3': 0.25, 'FsF-R1-01MD-4': 0.25, 'FsF-R1.1-01M-1': 1.0,
    'FsF-R1.1-01M-2': 1.0, 'FsF-R1.2-01M-1': 0.5, 'FsF-R1.2-01M-2': 0.5,
    'FsF-R1.3-01M-1': 1.0, 'FsF-R1.3-01M-2': 1.0, 'FsF-R1.3-01M-3': 1.0,
    'FsF-R1.3-02D-1': 0.0, 'FsF-R1.3-02D-1a': 0.0, 'FsF-R1.3-02D-1b': 0.0, 'FsF-R1.3-02D-1c': 0.0
}


def get_result_score(name_of_fuji_result_json: str = "fuji_result.json") -> Dict[str, float]:
    with open(name_of_fuji_result_json, "r", encoding="utf-8") as file:
        # Read the contents of the file
        json_content = file.read()
        json_data = json.loads(json_content)
        score_percent = json_data["summary"]["score_percent"]
        object_identifier = json_data["request"]["object_identifier"]
        # write_result_to_csv(object_identifier, score_percent)
        return score_percent


def map_json_to_metrics(json_input: Dict[str, Any]) -> Dict[str, float]:
    metric_test_mapping = {
        "FsF-F1-01D": ["FsF-F1-01D-1", "FsF-F1-01D-2"],
        "FsF-F1-02D": ["FsF-F1-02D-1", "FsF-F1-02D-2"],
        "FsF-F2-01M": ["FsF-F2-01M-1", "FsF-F2-01M-2", "FsF-F2-01M-3"],
        "FsF-F3-01M": ["FsF-F3-01M-1", "FsF-F3-01M-2"],
        "FsF-F4-01M": ["FsF-F4-01M-1", "FsF-F4-01M-2"],
        "FsF-A1-01M": ["FsF-A1-01M-1", "FsF-A1-01M-2", "FsF-A1-01M-3"],
        "FsF-A1-02M": ["FsF-A1-02M-1"],
        "FsF-A1-03D": ["FsF-A1-03D-1"],
        "FsF-I1-01M": ["FsF-I1-01M-1", "FsF-I1-01M-2"],
        "FsF-I2-01M": ["FsF-I2-01M-1", "FsF-I2-01M-2"],
        "FsF-I3-01M": ["FsF-I3-01M-1", "FsF-I3-01M-2"],
        "FsF-R1-01MD": ["FsF-R1-01MD-1", "FsF-R1-01MD-1a", "FsF-R1-01MD-1b", "FsF-R1-01MD-2", "FsF-R1-01MD-2a", "FsF-R1-01MD-2b", "FsF-R1-01MD-3", "FsF-R1-01MD-4"],
        "FsF-R1.1-01M": ["FsF-R1.1-01M-1", "FsF-R1.1-01M-2"],
        "FsF-R1.2-01M": ["FsF-R1.2-01M-1", "FsF-R1.2-01M-2"],
        "FsF-R1.3-01M": ["FsF-R1.3-01M-1", "FsF-R1.3-01M-2", "FsF-R1.3-01M-3"],
        "FsF-R1.3-02D": ["FsF-R1.3-02D-1", "FsF-R1.3-02D-1a", "FsF-R1.3-02D-1b", "FsF-R1.3-02D-1c"]
    }

    mapped_results = {}

    for result in json_input.get("results", []):
        metric_id = result["metric_identifier"]
        if metric_id in metric_test_mapping:
            for sub_metric in metric_test_mapping[metric_id]:
                score = result["score"]["earned"] / result["score"]["total"]
                mapped_results[sub_metric] = score

    return mapped_results


def write_result_to_csv(object_identifier, score_percent):
    with open("fuji_result.csv", "w", newline='', encoding="utf-8") as csv_file:
        # Create CSV writer with custom delimiter
        writer = csv.writer(csv_file, delimiter=';')
        # Write header row
        writer.writerow(["Object Identifier"] + list(score_percent.keys()))
        # Format score percentages as strings with two decimal places
        formatted_scores = [f'{score:.2f}' for score in score_percent.values()]
        # Write data row
        writer.writerow([object_identifier] + formatted_scores)


def evaluate(data_doi=None):
    data = data_example
    if data_doi:
        data["object_identifier"] = data_doi
    print(f"running fuji evaluation for {data}")

    try:
        response = requests.post(FUJI_URL, json=data, headers=headers, auth=fuji_auth, timeout=30)
        response.raise_for_status()
    except ConnectTimeout:
        print(f"Request timed out when trying to connect to {FUJI_URL}")
        return
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return

    if response.status_code == 200:
        print("Request successful!")
        parsed_response = json.loads(response.text)
        # Save the response content to a local file
        with open('fuji_result.json', 'w+', encoding="utf-8") as file:
            file.write(json.dumps(parsed_response, indent=4))
            print("Result saved to 'fuji_result.json'")
    else:
        print(f"Request failed with status code {response.status_code}")
        print(response.text)


def fuji_evaluate_to_list(data_doi=None) -> Dict[str, float]:
    data = data_example
    if data_doi:
        data["object_identifier"] = data_doi
    print(f"Running F-UJI evaluation for {data}")

    try:
        response = requests.post(FUJI_URL, json=data, headers=headers, auth=fuji_auth, timeout=30)
        response.raise_for_status()
    except ConnectTimeout:
        print(f"Request timed out when trying to connect to {FUJI_URL}")  # Debugging
        raise RuntimeError("FUJI API is unreachable (timeout).")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")  # Debugging
        raise RuntimeError(f"FUJI API request failed: {e}")

    if response.status_code == 200:
        print("Request successful!")
        parsed_response = response.json()
        return map_json_to_metrics(parsed_response)
    else:
        print(f"Request failed with status code {response.status_code}")
        raise RuntimeError(f"FUJI API request failed with status {response.status_code}")


def example_fuji_results() -> Any:
    file_path = "output/examples/FUJI_10.20387_bonares-1ttx-ng98.json"  # Replace with your actual file path
    with open(file_path, 'r', encoding='utf-8') as file:
        parsed_response = json.load(file)
    return map_json_to_metrics(parsed_response)


if __name__ == "__main__":
    # evaluate("10.20387/bonares-q82e-t008-test")
    # print(get_result_score())
    #
    # with open('fuji_result.json', 'r', encoding='utf-8') as f:
    #     json_data = json.load(f)
    #
    # mapped_metrics = map_json_to_metrics(json_data)
    # for metric, score in mapped_metrics.items():
    #     print(f"{metric}: {score}")

    print(example_fuji_results())
