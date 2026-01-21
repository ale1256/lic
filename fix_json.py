import json
import glob
import os

# Find all fMRI JSON files recursively inside bids_dataset
files = glob.glob("bids_dataset/**/*bold.json", recursive=True)

print(f"Found {len(files)} JSON files to check.")

for filepath in files:
    try:
        # 1. Read the file
        with open(filepath, "r") as f:
            data = json.load(f)

        # 2. Add the missing RepetitionTime
        data["RepetitionTime"] = 2.4

        # 3. Save the file back
        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)

        print(f"Fixed: {filepath}")

    except Exception as e:
        print(f"Error reading {filepath}: {e}")

print("Done! All files updated.")
