import numpy as np
import nibabel as nib
import os
from nilearn.datasets import load_mni152_template

def create_visible_mock(filename, contrast_level="high"):
    print(f"🧠 Generating Visible Mock: {filename}...")
    
    # 1. Load the Standard MNI Brain (so it looks like a real brain)
    try:
        mni = load_mni152_template()
        data_3d = mni.get_fdata()
        affine = mni.affine
    except Exception as e:
        print(f"❌ Error: Could not load MNI template. {e}")
        return

    # 2. Simulate Time (4D) for the analysis code
    # We repeat the brain volume 5 times
    n_timepoints = 10
    data_4d = np.repeat(data_3d[..., np.newaxis], n_timepoints, axis=3)

    # 3. Add Variability (Noise) so the analysis has something to calculate
    # We add noise ONLY where there is already brain tissue (data > 0)
    mask = data_4d > 0
    noise = np.random.randn(*data_4d.shape) * 200  # High amplitude noise
    
    # Combine: Base Brain + Noise
    final_data = data_4d.copy()
    final_data[mask] += noise[mask]

    # 4. CRITICAL: Normalization for Viewer
    # The viewer typically expects values between 0 and ~200. 
    # If values are 0.001 or 50000, it looks black.
    # We force the data into the 0-100 range.
    final_data = np.abs(final_data) # Remove negatives
    max_val = np.max(final_data)
    if max_val > 0:
        final_data = (final_data / max_val) * 100

    # 5. Save
    img = nib.Nifti1Image(final_data, affine)
    nib.save(img, filename)
    print(f"✅ Saved: {filename}")

if __name__ == "__main__":
    if not os.path.exists('mocks'):
        os.makedirs('mocks')

    # Create distinct files
    create_visible_mock("mocks/mock_visible_PD.nii.gz")
    create_visible_mock("mocks/mock_visible_HC.nii.gz")
    
    print("\n🚀 DONE! Upload these specific files to your app.")