import csv
import os
import re
from datetime import datetime
import FES_evaluation
import FUJI_evaluation
from requests.exceptions import ConnectTimeout
import tkinter as tk
from tkinter import filedialog

from doi_to_dqv import create_dqv_representation

cwd = os.getcwd()

file_path = os.path.join(cwd, r"metafiles\\metafiles_list.txt")


def get_identifier(line_str: str) -> str:
    # Regular expression pattern for matching DOIs
    pattern = r'\b(10\.\d{4,}(?:\.\d+)*\/\S+(?:(?![\"&\'<>])\S)*)\b'

    # Find the first match in the text
    match = re.search(pattern, line_str)
    if not match:
        # Define a regular expression pattern to match the URL
        pattern = r'(https?://\S+)'
        # Use re.search to find the first match of the pattern in the line
        match = re.search(pattern, line_str)
    # Return the matched DOI or None if no match is found
    return match.group(1) if match else None


# Open the file in read mode
def read_file_to_list(file_filepath: str = file_path) -> list:
    lines = []
    with open(file_filepath, 'r') as file:
        # Read each line
        for line in file:
            lines.append(line)
        return lines


def count_lines(file_io):
    line_count = sum(1 for _ in file_io)
    file_io.seek(0)
    return line_count


def format_time(seconds):
    """Formats time in seconds to hours, minutes, and seconds."""
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours)} hour{'s' if hours != 1 else ''}, {int(minutes)} minute{'s' if minutes != 1 else ''}, {seconds:.2f} second{'s' if seconds != 1 else ''}"


def run_on_list_of_pids():
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    filepath_2 = filedialog.askopenfilename(title="Select a CSV file", initialdir=os.path.join(cwd, "input"))

    with (open(filepath_2, "r", encoding="utf-8", newline="") as file):
        reader = csv.reader(file, delimiter=";")
        filepath_result = filepath_2.replace(".csv", "_result.csv")
        filepath_result = filepath_result.replace("input", "output")
        len_file = count_lines(file)
        with open(filepath_result, "w", encoding="utf-8") as result:
            headers = ("Dataset Name;Object Identifier;F1: FAIR Metrics Gen2- Unique Identifier;F1: FAIR Metrics Gen2 "
                       "- Identifier Persistence;F1: FAIR Metrics Gen2 - Data Identifier "
                       "Persistence;F2: FAIR Metrics Gen2 - Structured Metadata;F2: FAIR Metrics Gen2 - Grounded "
                       "Metadata;F3: FAIR Metrics Gen2 - Data Identifier Explicitly In "
                       "Metadata;F3: FAIR Metrics Gen2- Metadata Identifier Explicitly In Metadata;F4: FAIR Metrics "
                       "Gen2 - Searchable in major search engine;A1.1: FAIR Metrics Gen2 - Uses open free protocol "
                       "for data retrieval;A1.1: FAIR Metrics Gen2 - Uses open free protocol for metadata "
                       "retrieval;A1.2: FAIR Metrics Gen2 - Data authentication and authorization;A1.2: FAIR Metrics "
                       "Gen2 - Metadata authentication and authorization;A2: FAIR Metrics Gen2 - Metadata "
                       "Persistence;I1: FAIR Metrics Gen2 - Metadata Knowledge Representation Language (weak);I1: "
                       "FAIR Metrics Gen2 - Metadata Knowledge Representation Language (strong);I1: FAIR Metrics Gen2 "
                       "- Data Knowledge Representation Language (weak);I1: FAIR Metrics Gen2 - Data Knowledge "
                       "Representation Language (strong);I2: FAIR Metrics Gen2"
                       "- Metadata uses FAIR vocabularies (weak);I2: FAIR Metrics Gen2 - Metadata uses FAIR "
                       "vocabularies (strong);I3: FAIR Metrics Gen2 - Metadata contains qualified outward "
                       "references);R1.1: FAIR Metrics Gen2 - Metadata Includes License (strong);R1.1: FAIR Metrics "
                       "Gen2 - Metadata Includes License (weak);Average;;A;F;I;R;A1;F1;F2;F3;F4;I1;I2"
                       ";I3;R1;R1.1;R1.2;R1.3;FAIR")
            result.write(headers + "\n")

            # Save start time
            start_time = datetime.now()

            for index, line in enumerate(reader, start=1):
                current_time = datetime.now().strftime('%H:%M')  # Current hour and minute
                print(f"{current_time} - Processing line {index} of {len_file}:\\n{line}")
                identifier = line[1]
                print(f"found identifier: {identifier}")
                if identifier:
                    FES_evaluation.evaluate(identifier)
                    result_score_wilkinson = FES_evaluation.get_result_score()
                    try:
                        FUJI_evaluation.evaluate(identifier)
                        result_score_fuji = FUJI_evaluation.get_result_score()
                        fuji_values = [str(value) for value in result_score_fuji.values()]
                        fuji_success = True
                    except ConnectTimeout:
                        fuji_success = False
                        print("Connection timed out while evaluating.")
                        # Handle the timeout error gracefully
                    else:
                        print("Evaluation completed successfully.")

                    if fuji_success:
                        print(f"result scores: {result_score_wilkinson}, {result_score_fuji}")
                        newline = line[0].rstrip() + ";" + line[1].rstrip() + ";" + ";".join(
                            result_score_wilkinson) + ";" + ";" + ";".join(fuji_values)
                    else:
                        print(f"result scores: {result_score_wilkinson}")
                        newline = line[0].rstrip() + ";" + line[1].rstrip() + ";" + ";".join(
                            result_score_wilkinson)
                    result.write(newline + "\n")

            # Save end time
            end_time = datetime.now()

            # Calculate total processing time
            processing_time = end_time - start_time
            processing_time_seconds = processing_time.total_seconds()

            # Calculate processing time per line
            time_per_line = processing_time_seconds / len_file if len_file else 0

            # Format total processing time and processing time per line for display
            formatted_total_time = format_time(processing_time_seconds)
            formatted_time_per_line = format_time(time_per_line)

            print(f"Total processing time: {formatted_total_time}.")
            print(f"Average processing time per line: {formatted_time_per_line}.")


def csv_list_to_dqv():
    root = tk.Tk()
    root.withdraw()

    input_file_path = filedialog.askopenfilename(
        title="Select Input CSV File",
        filetypes=[("CSV files", "*.csv")],
        initialdir=os.path.join(cwd, "input")
    )

    if not input_file_path:
        print("No input file selected.")
        return

    output_dir = filedialog.askdirectory(
        title="Select Output Directory",
        initialdir=os.path.join(cwd, "output")
    )

    if not output_dir:
        print("No output directory selected.")
        return

    # Attempt to open the file with UTF-7 encoding
    try:
        with open(input_file_path, "r", encoding="utf-7", newline="") as file:
            reader = csv.reader(file, delimiter=",", quotechar='"', skipinitialspace=True)
            lines = list(reader)
    except UnicodeDecodeError:
        # If UTF-7 fails, fallback to UTF-8
        with open(input_file_path, "r", encoding="utf-8", newline="") as file:
            reader = csv.reader(file, delimiter=",", quotechar='"', skipinitialspace=True)
            lines = list(reader)

    len_file = len(lines)
    for index, line in enumerate(lines, start=1):
        print(f"{index}: {line}")
        current_time = datetime.now().strftime('%H:%M')
        start_time = datetime.now()
        print(f"{current_time} - Processing line {index} of {len_file}:\n{line}")
        identifier = line[1]
        print(f"found identifier: {identifier}")

        if identifier:
            try:
                fes_results = FES_evaluation.fes_evaluate_to_list(identifier)
                fes_success = True
            except ConnectTimeout:
                fes_success = False
                print("FES Connection timed out while evaluating.")

            try:
                fuji_results = FUJI_evaluation.fuji_evaluate_to_list(identifier)
                result_score_fuji = FUJI_evaluation.get_result_score()
                fuji_success = True
            except ConnectTimeout:
                fuji_success = False
                print("FUJI Connection timed out while evaluating.")
            else:
                print("Evaluation completed successfully.")

            end_time = datetime.now()

            if fuji_success and fes_success:
                sanitized_identifier = re.sub(r"[^\w\-_.]", "_", identifier)
                graph = create_dqv_representation(
                    identifier,
                    fes_results or [],
                    fuji_results or {},
                    start_time,
                    end_time
                )

                turtle_file_path = os.path.join(output_dir, f"{sanitized_identifier}_dqv.ttl")
                graph.serialize(destination=turtle_file_path, format="turtle")
                print(f"Graph written to {turtle_file_path}")


if __name__ == "__main__":
    # run_on_list_of_pids()
    csv_list_to_dqv()
