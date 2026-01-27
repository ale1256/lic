import numpy as np
import nibabel as nib
import os
from nilearn.datasets import load_mni152_template
from nilearn.image import resample_to_img

def create_realistic_mock(filename):
    print(f"Generating Realistic Mock: {filename}...")
    
    # 1. Load Standard MNI Template (Standard Brain)
    try:
        mni = load_mni152_template()
        data = mni.get_fdata()
        affine = mni.affine
    except Exception as e:
        print(f"Error downloading MNI template: {e}")
        return

    # 2. Simulate 4D fMRI Data (Time Series)
    # We repeat the brain volume 10 times to simulate time
    n_timepoints = 10 
    data_4d = np.repeat(data[..., np.newaxis], n_timepoints, axis=3)

    # 3. Add "Biological" Noise
    # We create noise but mask it so it only appears INSIDE the brain, not the background
    noise = np.random.randn(*data_4d.shape) * 10 
    
    # Create a binary mask from the template (where value > 0)
    # Broadcast mask to 4D to match data shape
    brain_mask = (data > 0).astype(int)
    brain_mask_4d = np.repeat(brain_mask[..., np.newaxis], n_timepoints, axis=3)
    
    # Apply noise only to brain areas
    masked_noise = noise * brain_mask_4d
    
    # Add noise to base data and ensure positive values
    final_data = data_4d + masked_noise
    final_data[final_data < 0] = 0 # MRI signals are positive
    
    # 4. Intensity Scaling for Viewer
    # The Niivue viewer in your HTML expects values roughly between 0-150.
    # We normalize the data to be clearly visible.
    max_val = np.max(final_data)
    if max_val > 0:
        final_data = (final_data / max_val) * 150

    # 5. Save as NIfTI
    img = nib.Nifti1Image(final_data, affine)
    nib.save(img, filename)
    print(f"✅ Successfully created: {filename}")

if __name__ == "__main__":
    if not os.path.exists('mocks'):
        os.makedirs('mocks')
    
    # Create one "Parkinson's" mock and one "Control" mock
    # (Note: These are random, but valid files for the pipeline)
    create_realistic_mock("mocks/mock_patient_PD.nii.gz")
    create_realistic_mock("mocks/mock_control_HC.nii.gz")
    
    print("\nDONE! Upload these files via the 'Upload Scan' page.")