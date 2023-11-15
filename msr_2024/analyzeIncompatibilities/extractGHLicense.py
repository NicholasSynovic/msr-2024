import os
import json
import pandas as pd
import sys
import re

# Specify the folder containing the JSON files
json_folder = "../../../scancode_licenses/" 

# Files to look at
locations = ["license", "license.txt", "license.md", "license.rst", 
            "readme", "readme.txt", "readme.md", "readme.rst"]

# Initialize a dictionary to store the results
results = {}

# Get a list of JSON files in the folder
json_files = [json_file for json_file in os.listdir(json_folder) if json_file.endswith(".json")]
json_files = json_files[1:] # first file creates major errors

# Get the total number of JSON files
total_json_files = len(json_files)

# Initialize the counter string, for displaying progress
counter_str = ""

# license parsing function
def parse_licenses(license_string):
    # Split the string on 'AND' or 'OR', and remove leading/trailing whitespaces
    terms = [term.strip() for term in re.split(r'\b(?:AND|OR)\b', license_string)]

    # Remove parentheses from terms
    terms = [term.strip('()') for term in terms]

    # Remove empty terms
    terms = [term for term in terms if term]

    return terms

# Iterate through the JSON files in the folder
for i, json_file in enumerate(json_files, start=1):
    repo_name = os.path.splitext(json_file)[0]
    file_path = os.path.join(json_folder, json_file)

    # Load data from the JSON file as text
    with open(file_path, 'r', encoding='utf-8') as f:
        json_data = f.read()

    # Initialize a list to store unique detected licenses for this repository
    unique_licenses = []

    # Attempt to load the JSON data as a Python dictionary
    try:
        json_dict = json.loads(json_data)
    except json.JSONDecodeError as e:
        # If decoding fails, set the value to None
        print(f"Error decoding {json_file}: {e}")
        json_dict = None

    if json_dict is not None:
        files_list = json_dict["files"]
        for file in files_list:
            matches = any(re.search(location, file["path"], re.IGNORECASE) for location in locations)
            if(matches and file["detected_license_expression"] is not None):
                unique_licenses.extend(parse_licenses(file["detected_license_expression"]))
                continue

    # If no unique licenses were found, set the value to None
    if not unique_licenses:
        unique_licenses = None
    else:
        unique_licenses = list(set(unique_licenses))

    # Store the unique licenses for this repository in the results dictionary
    results[repo_name.replace("_", "/", 1)] = unique_licenses # replace first occurence of "_" with "/" in the repo name since github usernames are not allowed to have "_" in them, thus the "_" in the repo name is the stand in for "/" 

    # Update the counter string
    counter_str = f"\rProcessed {i}/{total_json_files} JSON files"
    sys.stdout.write(counter_str)
    sys.stdout.flush()

# Add a newline after the counter
print()

# Save the results to a JSON file
with open("all_gh_licenses.json", "w") as output_file:
    json.dump(results, output_file, indent=2)

print("Results saved to all_gh_licenses.json")
