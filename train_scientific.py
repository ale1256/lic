import os
import glob
import numpy as np
import joblib
import nibabel as nib
import warnings
from nilearn import datasets, maskers, connectome
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

warnings.filterwarnings("ignore")

def train_scientific():
    BASE_DIR = os.getcwd()
    PD_DIR = os.path.join(BASE_DIR, "research_data", "PD")
    HC_DIR = os.path.join(BASE_DIR, "research_data", "HC")
    MODEL_DEST = os.path.join(BASE_DIR, "diagnosis", "ml_models", "pd_classifier.pkl")

    print("🧠 Pasul 1: Extracție Semnale...")
    atlas = datasets.fetch_atlas_msdl()
    masker = maskers.NiftiMapsMasker(
        maps_img=atlas.maps, 
        standardize='zscore_sample',
        detrend=True,
        resampling_target='maps',
        memory='nilearn_cache'
    )

    X_features = []
    y_labels = []
    categories = [("PD", PD_DIR, 1), ("HC", HC_DIR, 0)]

    for label_name, directory, label_val in categories:
        if not os.path.exists(directory): continue
        files = glob.glob(os.path.join(directory, "*.nii*"))
        for f in files:
            try:
                img = nib.load(f)
                if len(img.shape) < 4 or img.shape[3] < 10: continue
                
                print(f"  > Procesare: {os.path.basename(f)}")
                ts = masker.fit_transform(f)
                
                # Folosim Correlation cu vectorizare pentru compatibilitate maxima
                conn = connectome.ConnectivityMeasure(kind='correlation', vectorize=True, discard_diagonal=True)
                vector = conn.fit_transform([ts])[0]
                
                X_features.append(vector)
                y_labels.append(label_val)
            except Exception as e:
                print(f"  ❌ Eroare la {os.path.basename(f)}: {e}")

    if len(set(y_labels)) < 2:
        print("❌ Date insuficiente (minim 1 PD si 1 HC).")
        return

    X = np.array(X_features)
    y = np.array(y_labels)

    print(f"📊 Dataset: {X.shape[0]} subiecți. Antrenare Pipeline...")

    # Pipeline robust pentru seturi mici
    model = Pipeline([
        ('scaler', StandardScaler()),
        ('svm', SVC(kernel='linear', C=1.0, probability=True, class_weight='balanced'))
    ])

    model.fit(X, y)

    os.makedirs(os.path.dirname(MODEL_DEST), exist_ok=True)
    joblib.dump(model, MODEL_DEST)
    print(f"✅ SUCCES! Model salvat în: {MODEL_DEST}")

if __name__ == "__main__":
    train_scientific()