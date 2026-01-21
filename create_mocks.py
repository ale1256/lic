import numpy as np
import nibabel as nib
import os
from nilearn.datasets import load_mni152_template

def create_realistic_mock(filename):
    print(f"Generare Mock Realistic: {filename}...")
    try:
        mni = load_mni152_template()
        data = mni.get_fdata()
        affine = mni.affine
    except Exception as e:
        print(f"Eroare la descarcarea MNI: {e}")
        return

    n_timepoints = 10
    data_4d = np.repeat(data[..., np.newaxis], n_timepoints, axis=3)

    noise = np.random.randn(*data_4d.shape) * 5 
    data_4d = data_4d + noise
    
    img = nib.Nifti1Image(data_4d, affine)
    nib.save(img, filename)
    print(f" Creat cu succes: {filename}")

if __name__ == "__main__":
    if not os.path.exists('mocks'):
        os.makedirs('mocks')
    create_realistic_mock("mocks/test_patient_PD_RealBrain.nii.gz")
    create_realistic_mock("mocks/test_control_HC_RealBrain.nii.gz")
    
    print("\nDONE! Aceste fisiere sunt gata de upload in aplicatie.")