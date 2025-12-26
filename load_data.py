import json
from pathlib import Path

def dump_application_information(application_information):
    FILE = "all_applications.json"

    # Load existing data
    if Path(FILE).exists():
        with open(FILE, "r") as f:
            data = json.load(f)
    else:
        data = []

    # Append new application
    data.append(application_information.dict())

    # Save back
    with open(FILE, "w") as f:
        json.dump(data, f, indent=2)

def delete_json_file(json_file: str):
    """
    Deletes the specified JSON file if it exists.
    """
    path = Path(json_file)
    if path.exists():
        path.unlink()
        print(f"Deleted JSON file '{json_file}'.")
    else:
        print(f"JSON file '{json_file}' not found.")