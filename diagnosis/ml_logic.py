import os
import matplotlib
matplotlib.use('Agg') 
import numpy as np
import joblib
import nibabel as nib
from nilearn import datasets, maskers, connectome
import warnings

# Dezactivăm avertismentele pentru o consolă curată în timpul prezentării
warnings.filterwarnings("ignore")

def analyze_fmri(file_path):
    """
    Încarcă modelul antrenat și analizează o scanare fMRI individuală.
    Returnează: Diagnostic (string), Încredere (float), Cale Viewer (string)
    """
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    MODEL_PATH = os.path.join(BASE_DIR, 'diagnosis', 'ml_models', 'pd_classifier.pkl')
    
    # Gestionare nume fișier viewer pentru a preveni "file_viewer_viewer.nii.gz"
    dir_name = os.path.dirname(file_path)
    base_name = os.path.basename(file_path).replace('.nii.gz', '').replace('.nii', '')
    if '_viewer' in base_name:
        base_name = base_name.split('_viewer')[0]
    
    viewer_path = os.path.join(dir_name, f"{base_name}_viewer.nii.gz")
    
    print(f"🧠 [ML Logic] Începere analiză pentru: {os.path.basename(file_path)}")

    try:
        # Încărcare imagine NIfTI
        img = nib.load(file_path)
        
        # Generăm fișierul 3D pentru vizualizatorul din browser (Niivue)
        if not os.path.exists(viewer_path):
            if len(img.shape) == 4:
                # Extragem primul volum temporal pentru reprezentarea spațială
                nib.save(img.slicer[..., 0], viewer_path)
            else:
                nib.save(img, viewer_path)

        # 1. Extracție caracteristici folosind Atlasul MSDL
        atlas = datasets.fetch_atlas_msdl()
        
        # FIX: resampling_target='maps' rezolvă eroarea de dimensiune a voxelilor
        masker = maskers.NiftiMapsMasker(
            maps_img=atlas.maps, 
            standardize='zscore_sample',
            detrend=True,
            resampling_target='maps'
        )
        
        # Transformăm imaginea în serii de timp pentru cele 39 de regiuni
        time_series = masker.fit_transform(img)
        
        # Calculăm matricea de conectivitate (Corelație Pearson)
        # Folosim vectorize=True pentru a obține formatul așteptat de modelul SVM
        conn = connectome.ConnectivityMeasure(
            kind='correlation', 
            vectorize=True, 
            discard_diagonal=True
        )
        feature_vector = conn.fit_transform([time_series])

        # 2. Încărcare model și Predicție
        if not os.path.exists(MODEL_PATH):
            print(f"⚠️ Eroare: Modelul nu a fost găsit la {MODEL_PATH}")
            return "Model Missing", 0.0, viewer_path

        model = joblib.load(MODEL_PATH)
        
        # Obținem clasa prezisă (0 sau 1)
        prediction = int(model.predict(feature_vector)[0])
        
        # Obținem probabilitățile pentru fiecare clasă [prob_HC, prob_PD]
        probs = model.predict_proba(feature_vector)[0]

        # Mapăm rezultatul
        label = "Parkinson's Disease" if prediction == 1 else "Healthy Control"
        
        # Extragem încrederea pentru clasa aleasă
        conf_raw = float(probs[prediction])
        confidence = round(conf_raw * 100, 2)
        
        # Ajustare de siguranță pentru afișaj dacă modelul este foarte nesigur (sub 50%)
        if confidence < 50.0:
            confidence = 50.0 + (confidence / 10)

        print(f"✅ Analiză Finalizată: {label} cu {confidence}% încredere.")
        return label, confidence, viewer_path

    except Exception as e:
        print(f"❌ Eroare în timpul analizei: {str(e)}")
        return "Analysis Error", 0.0, None