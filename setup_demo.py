import os
import numpy as np
import nibabel as nib
import joblib
from nilearn import datasets, maskers, connectome
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

def create_structured_mock(file_path, diagnosis='PD'):
    
    n_regions = 39
    n_volumes = 50
    
    if diagnosis == 'PD':
        signals = np.random.randn(n_volumes, n_regions)
        signals[:, 1] = signals[:, 0] 
    else:
        signals = np.random.randn(n_volumes, n_regions)

    data = np.zeros((10, 10, 10, n_volumes))
    for i in range(n_regions):
        x, y, z = i % 10, (i // 10) % 10, i // 100
        data[x, y, z, :] = signals[:, i]

    img = nib.Nifti1Image(data.astype(np.float32), np.eye(4))
    nib.save(img, file_path)
    print(f" Creat fișier {diagnosis}: {file_path}")

def train_demo_model():
    print(" Antrenare model bazat pe conectivitate...")

    X_pd = np.random.normal(0, 0.1, (10, 741))
    X_pd[:, 0] = 1.5 
    
    X_hc = np.random.normal(0, 0.1, (10, 741))
    X_hc[:, 0] = -1.5
    
    X = np.vstack([X_pd, X_hc])
    y = np.array([1]*10 + [0]*10)
    
    model = Pipeline([
        ('scaler', StandardScaler()),
        ('svm', SVC(kernel='linear', probability=True))
    ])
    
    model.fit(X, y)
    
    dest_path = os.path.join('diagnosis', 'ml_models', 'pd_classifier.pkl')
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    joblib.dump(model, dest_path)
    print(f"🚀 Model salvat: {dest_path}")

if __name__ == "__main__":

    os.makedirs('mocks', exist_ok=True)
    
    create_structured_mock('mocks/pacient_pozitiv_PD.nii.gz', 'PD')
    create_structured_mock('mocks/subiect_sanatos_HC.nii.gz', 'HC')
    
    train_demo_model()
    
    print("1. Upload 'pacient_pozitiv_PD.nii.gz' -> Parkinson's")
    print("2. Upload 'subiect_sanatos_HC.nii.gz' -> Healthy") 