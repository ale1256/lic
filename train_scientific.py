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
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.model_selection import LeaveOneOut, cross_val_predict
from sklearn.metrics import accuracy_score, balanced_accuracy_score, roc_auc_score

warnings.filterwarnings("ignore")

def train_scientific():
    BASE_DIR = os.getcwd()
    PD_DIR = os.path.join(BASE_DIR, "research_data", "PD")
    HC_DIR = os.path.join(BASE_DIR, "research_data", "HC")
    MODEL_DEST = os.path.join(BASE_DIR, "diagnosis", "ml_models", "pd_classifier.pkl")

    print("🧠 Pasul 1: Inițializare Atlas MSDL...")
    atlas = datasets.fetch_atlas_msdl()
    masker = maskers.NiftiMapsMasker(
        maps_img=atlas.maps, 
        standardize='zscore_sample',
        detrend=True,
        memory='nilearn_cache'
    )

    all_time_series = [] 
    y_labels = []        
    
    categories = [("PD", PD_DIR, 1), ("HC", HC_DIR, 0)]

    print("📂 Pasul 2: Extracție serii de timp...")
    for label_name, directory, label_val in categories:
        if not os.path.exists(directory):
            print(f"⚠️ Folderul {label_name} lipsește.")
            continue
            
        files = glob.glob(os.path.join(directory, "*.nii*"))
        print(f"🔎 Am găsit {len(files)} fișiere în {label_name}.")
        
        for f in files:
            try:
                img = nib.load(f)
                if len(img.shape) < 4:
                    print(f"  ⏭️ Skip (3D Image): {os.path.basename(f)} - Conectivitatea necesită date 4D.")
                    continue
                
                if img.shape[3] < 10:
                    print(f"   Skip (Too short): {os.path.basename(f)} - Prea puține volume temporale ({img.shape[3]}).")
                    continue

                print(f"  > Procesare semnal 4D: {os.path.basename(f)}")
                ts = masker.fit_transform(f)
                if ts.ndim == 2:
                    all_time_series.append(ts)
                    y_labels.append(label_val)
                else:
                    print(f"  ⚠️ Format invalid după filtrare pentru {os.path.basename(f)}")
                    
            except Exception as e:
                print(f"   Eroare la citirea {os.path.basename(f)}: {e}")

    if len(all_time_series) < 2 or len(set(y_labels)) < 2:
        print("\n Date insuficiente pentru antrenare.")
        print(f"   Subiecți procesați corect: {len(all_time_series)}")
        print("   Asigură-te că ai fișiere fMRI 4D reale în ambele foldere (PD și HC).")
        return

    print(f"\n📈 Pasul 3: Calcul Conectivitate Corelație pentru {len(all_time_series)} subiecți...")
    try:

        conn = connectome.ConnectivityMeasure(kind='correlation', vectorize=True, discard_diagonal=True)
        X_features = conn.fit_transform(all_time_series)
        y = np.array(y_labels)
        
        print(f" Dataset creat: {X_features.shape[0]} subiecți și {X_features.shape[1]} conexiuni.")

        model = Pipeline([
            ('scaler', StandardScaler()),
            ('feature_selection', SelectKBest(f_classif, k=min(50, X_features.shape[1]))),
            ('svm', SVC(kernel='linear', C=1.0, probability=True, class_weight='balanced'))
        ])

        if X_features.shape[0] < 10:
            print("⚠️ Set foarte mic. Rulez Leave-One-Out pentru o evaluare minimă.")
            loo = LeaveOneOut()
            y_pred = cross_val_predict(model, X_features, y, cv=loo, method='predict')
            y_prob = cross_val_predict(model, X_features, y, cv=loo, method='predict_proba')[:, 1]
            acc = accuracy_score(y, y_pred)
            bacc = balanced_accuracy_score(y, y_pred)
            try:
                auc = roc_auc_score(y, y_prob)
            except Exception:
                auc = float('nan')
            print(f"🧪 LOOCV Accuracy: {acc:.2f} | Balanced Acc: {bacc:.2f} | ROC-AUC: {auc:.2f}")

        print("Antrenare Model Final pe toate datele...")
        model.fit(X_features, y)

        os.makedirs(os.path.dirname(MODEL_DEST), exist_ok=True)
        joblib.dump(model, MODEL_DEST)
        
        print(f" SUCCES! Modelul a fost salvat în: {MODEL_DEST}")
        
    except Exception as e:
        print(f" Eroare la calculul matricelor sau antrenare: {e}")

if __name__ == "__main__":
    train_scientific()
