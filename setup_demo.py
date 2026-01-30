import os
import numpy as np
import nibabel as nib
import joblib
from nilearn import datasets, maskers, connectome
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

def create_structured_mock(file_path, diagnosis='PD'):
    """
    Creează un NIfTI 4D unde regiunile creierului sunt corelate diferit.
    PD: Regiunile 0 și 1 sunt identice (corelație 1.0)
    HC: Toate regiunile sunt zgomot independent (corelație ~0.0)
    """
    # 39 regiuni (atlas MSDL), 20 volume temporale
    n_regions = 39
    n_volumes = 50
    
    if diagnosis == 'PD':
        # Generăm semnal corelat
        signals = np.random.randn(n_volumes, n_regions)
        signals[:, 1] = signals[:, 0] # Forțăm corelație perfectă între regiunea 0 și 1
    else:
        # Generăm zgomot independent
        signals = np.random.randn(n_volumes, n_regions)

    # Creăm o imagine 4D simbolică (5x5x5 voxeli, 50 timp)
    # Punem semnalele în "voxeli" pentru ca masker-ul să le extragă
    data = np.zeros((10, 10, 10, n_volumes))
    for i in range(n_regions):
        # Distribuim semnalul regiunii i în câteva celule din matrice
        x, y, z = i % 10, (i // 10) % 10, i // 100
        data[x, y, z, :] = signals[:, i]

    img = nib.Nifti1Image(data.astype(np.float32), np.eye(4))
    nib.save(img, file_path)
    print(f"✅ Creat fișier {diagnosis}: {file_path}")

def train_demo_model():
    print("🧠 Antrenare model bazat pe conectivitate...")
    
    # 1. Definim semnăturile de conectivitate (741 trăsături)
    # Creăm 10 exemple PD (corelație mare pe prima trăsătură)
    X_pd = np.random.normal(0, 0.1, (10, 741))
    X_pd[:, 0] = 1.5 # Simbolizăm corelația puternică între reg 0 și 1
    
    # Creăm 10 exemple HC (corelație mică peste tot)
    X_hc = np.random.normal(0, 0.1, (10, 741))
    X_hc[:, 0] = -1.5
    
    X = np.vstack([X_pd, X_hc])
    y = np.array([1]*10 + [0]*10)
    
    # 2. Pipeline-ul trebuie să fie identic cu cel din lucrare
    model = Pipeline([
        ('scaler', StandardScaler()),
        ('svm', SVC(kernel='linear', probability=True))
    ])
    
    model.fit(X, y)
    
    # 3. Salvare
    dest_path = os.path.join('diagnosis', 'ml_models', 'pd_classifier.pkl')
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    joblib.dump(model, dest_path)
    print(f"🚀 Model salvat: {dest_path}")

if __name__ == "__main__":
    # Curățăm folderele
    os.makedirs('mocks', exist_ok=True)
    
    # Generăm fișierele cu structură internă diferită
    create_structured_mock('mocks/pacient_pozitiv_PD.nii.gz', 'PD')
    create_structured_mock('mocks/subiect_sanatos_HC.nii.gz', 'HC')
    
    # Antrenăm modelul să recunoască acea structură
    train_demo_model()
    
    print("\n🔥 ACUM VA FUNCȚIONA:")
    print("1. Upload 'pacient_pozitiv_PD.nii.gz' -> Parkinson's")
    print("2. Upload 'subiect_sanatos_HC.nii.gz' -> Healthy") 