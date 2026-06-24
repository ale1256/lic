import os
import numpy as np
import nibabel as nib
import joblib
from sklearn.linear_model import LogisticRegression
from nilearn import datasets


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEDIA_DIR = os.path.join(BASE_DIR, 'media', 'scans')
MODEL_DIR = os.path.join(BASE_DIR, 'diagnosis', 'ml_models')

os.makedirs(MEDIA_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)

def step_1_create_model():
    print("1️⃣  Generating AI Model...")
    X = np.random.rand(50, 741)
    y = np.random.randint(0, 2, 50)
    model = LogisticRegression()
    model.fit(X, y)
    
    model_path = os.path.join(MODEL_DIR, 'pd_classifier.pkl')
    joblib.dump(model, model_path)
    print(f"   -> Model saved: {model_path}")

def step_2_download_atlas():
    try:
        atlas = datasets.fetch_atlas_msdl()
        print("   -> Atlas cached successfully.")
    except Exception as e:
        print(f"   -> Warning: Could not download atlas. Check internet. Error: {e}")

def step_3_create_standard_file():
    print("3️⃣  Creating Standard Brain File for Viewer...")
    try:
        mni = datasets.load_mni152_template()
        data = mni.get_fdata()
        affine = mni.affine
        
        test_path = os.path.join(MEDIA_DIR, 'test_standard.nii.gz')
        nib.save(mni, test_path)
        print(f"   -> Standard brain saved: {test_path}")
        
        mock_path = os.path.join(MEDIA_DIR, 'upload_me_visible.nii.gz')
        
        data_4d = np.repeat(data[..., np.newaxis], 10, axis=3)
        
        noise = np.random.randn(*data_4d.shape) * 200
        mask = data_4d > 0
        data_4d[mask] += noise[mask]
        
        data_4d = np.abs(data_4d)
        data_4d = (data_4d / np.max(data_4d)) * 100
        
        nib.save(nib.Nifti1Image(data_4d, affine), mock_path)
        print(f"   -> Uploadable mock saved: {mock_path}")
        
    except Exception as e:
        print(f"   -> Error creating files: {e}")

if __name__ == "__main__":
    print("--- STARTING FIXES ---")
    step_1_create_model()
    step_2_download_atlas()
    step_3_create_standard_file()
    print("--- DONE. RESTART YOUR SERVER ---")