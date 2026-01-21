#!/bin/bash

# 1. Clean up old dataset
echo "Cleaning up..."
rm -rf bids_dataset
mkdir -p bids_dataset

# 2. Create the Description File
echo '{"Name": "PPMI Thesis", "BIDSVersion": "1.0.2"}' > bids_dataset/dataset_description.json

# 3. Loop through your 4 healthy subjects
for sub in 118352 137450 140258 153191; do
    echo "========================================"
    echo "Processing Subject $sub..."
    
    # Create BIDS folders
    mkdir -p bids_dataset/sub-$sub/anat
    mkdir -p bids_dataset/sub-$sub/func

    # --- ANATOMICAL ---
    # Find the folder containing "MPRAGE" or "T1"
    anat_input=$(find test_batch/$sub -type d \( -name "*MPRAGE*" -o -name "*T1*" \) | head -n 1)
    
    # FIX: Naming strictly as sub-ID_T1w (No session label)
    dcm2niix -b y -z y -o bids_dataset/sub-$sub/anat -f sub-${sub}_T1w "$anat_input"

    # --- FUNCTIONAL ---
    # Find the folder containing "RESTING" or "BOLD"
    func_input=$(find test_batch/$sub -type d \( -name "*RESTING*" -o -name "*BOLD*" \) | head -n 1)
    
    # FIX: Naming strictly as sub-ID_task-rest_bold (No session label)
    dcm2niix -b y -z y -o bids_dataset/sub-$sub/func -f sub-${sub}_task-rest_bold "$func_input"

done

echo "========================================"
echo "Injecting RepetitionTime..."
# Force TR = 2.4s into all functional JSONs
find bids_dataset -name "*bold.json" -exec sed -i '' '1s/{/{\n  "RepetitionTime": 2.4,/' {} +

echo "DONE! Dataset is ready."
