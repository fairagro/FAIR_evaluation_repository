import re
import requests
import csv

from requests.exceptions import ConnectTimeout

# This is the Wilkinson FAIR Evaluation Service
url = 'https://fairdata.services:7171/FAIR_Evaluator/collections/6/evaluate'
headers = {
    'accept': '*/*',
    'Content-Type': 'application/json'
}
data_example = {
    "executor": "FAIRagro FAIR Assessment Tool Development",
    "resource": "10.20387/bonares-gx1f-bh69",
    # "resource": "https://atlas.thuenen.de/api/v2/resources?page_size=200&format=json",
    "title": "Test_Eval"
}

# Cached result for development
fes_evaluation_result_example = [
    '1', '1', '0', '1', '1', '0', '0', '0', '0', '1', '0', '1', '0', '1', '1',
    '0', '0', '1', '0', '1', '1', '1'
]

bonares_input = "input/bonares_dois.csv"
example_input = "input/simple_test.csv"


def get_result_score(name_of_wilkinson_result_html: str = "wilkinson_result.html") -> list:
    with open(name_of_wilkinson_result_html, "r", encoding="utf-8") as file:
        # Read the contents of the file
        html_content = file.read()

        # Find all occurrences of alt="5stars" with any number of stars (0-5)
        score_matches = re.findall(r'Score: (\d+)', html_content)

        # Convert the star ratings to integers and calculate the average
        total_score = sum(int(stars) for stars in score_matches)
        average_score = total_score / len(score_matches) if score_matches else 0

        # Multiply each score by 100
        score_matches = [str(int(score) * 100) for score in score_matches]
        average_score = int(round(average_score * 100, 3))  # Convert average score to integer

        # Append the average score to the list and return
        score_matches.append(str(average_score))
        return score_matches


def evaluate(data_doi=None):
    data = data_example
    if data_doi:
        data["resource"] = data_doi
    print(f"running FES evaluation for {data}")
    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        print("Request successful!")

        # Save the response content to a local file
        with open('wilkinson_result.html', 'w', encoding="utf-8") as file:
            file.write(response.content.decode('utf-8'))
            print("Result saved to 'wilkinson_result.html'")
    else:
        print(f"Request failed with status code {response.status_code}")


def fes_evaluate_to_list(data_doi=None):
    data = data_example
    if data_doi:
        data["resource"] = data_doi
    print(f"Running FES evaluation for {data}")

    try:
        response = requests.post(url, json=data, headers=headers, verify=True, timeout=120)
    except ConnectTimeout:
        print("Initial request timed out. Retrying with verify=False.")
        response = requests.post(url, json=data, headers=headers, verify=False, timeout=120)

    if response.status_code == 200:
        print("Request successful!")

        # Directly parsing the response content
        html_content = response.content.decode('utf-8')

        # Find all occurrences of Score: followed by a number
        score_matches = re.findall(r'Score: (\d+)', html_content)

        # Convert the scores to integers and calculate the average
        # total_score = sum(int(score) for score in score_matches)
        # average_score = total_score / len(score_matches) if score_matches else 0

        # Append the average score to the list and return
        # score_matches.append(str(average_score))
        print(f"fes_evaluate_to_list_result: {score_matches}")
        return score_matches

    else:
        print(f"Request failed with status code {response.status_code}")
        return None


def read_second_column(file_path):
    """
    Reads the second column of a CSV file with specified delimiter and encoding.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        list: A list of entries in the second column.
    """
    # Initialize an empty list to store the entries
    second_column_entries = []

    # Open the file in read mode with utf-8 encoding
    with open(file_path, mode='r', encoding='utf-8') as file:
        # Create a CSV reader object with the specified delimiter
        reader = csv.reader(file, delimiter=';')

        # Iterate over each row in the CSV file
        for row in reader:
            # Check if the row has at least two elements
            if len(row) >= 2:
                # Add the entry in the second column to the list
                second_column_entries.append(row[1])

    return second_column_entries


if __name__ == "__main__":
    dois_list = read_second_column(example_input)
    print("DOIs read from CSV:", dois_list)
    for doi in dois_list:
        print("Processing DOI:", doi)

        # evaluate(doi)
        # print(get_result_score())

        res_list = fes_evaluate_to_list(doi)
        print(res_list)
