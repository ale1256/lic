import os
import numpy as np
import joblib
import nibabel as nib
from nilearn import datasets, maskers, connectome
import warnings

warnings.filterwarnings("ignore")

def analyze_fmri(file_path):
    """
    Extrage un snapshot 3D clar și rulează analiza ML.
    """
    dir_name = os.path.dirname(file_path)
    base_name = os.path.basename(file_path)
    
    # Nume curat: evităm duplicarea _viewer_viewer
    clean_name = base_name.replace('.nii.gz', '').replace('.nii', '').replace('_viewer', '')
    viewer_filename = f"{clean_name}_viewer.nii.gz"
    viewer_path = os.path.join(dir_name, viewer_filename)

    try:
        # 1. Încărcare Creier
        img = nib.load(file_path)
        data = img.get_fdata()
        
        # 2. Generare Snapshot 3D (Volumul de control)
        if len(img.shape) == 4:
            # Alegem volumul 10 sau mijlocul (primele volume sunt adesea negre)
            idx = min(10, img.shape[3] - 1)
            snapshot_data = data[..., idx]
            # Creăm imaginea NIfTI nouă
            viewer_img = nib.Nifti1Image(snapshot_data, img.affine)
            nib.save(viewer_img, viewer_path)
            print(f"✅ Snapshot 3D generat la volumul {idx}")
        else:
            nib.save(img, viewer_path)

        # 3. Analiză ML
        atlas = datasets.fetch_atlas_msdl()
        masker = maskers.NiftiMapsMasker(
            maps_img=atlas.maps, 
            standardize='zscore_sample',
            detrend=True,
            resampling_target='maps'
        )
        
        time_series = masker.fit_transform(file_path)
        conn = connectome.ConnectivityMeasure(kind='correlation', vectorize=True, discard_diagonal=True)
        feature_vector = conn.fit_transform([time_series])

        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        MODEL_PATH = os.path.join(BASE_DIR, 'diagnosis', 'ml_models', 'pd_classifier.pkl')
        
        if not os.path.exists(MODEL_PATH):
            return "Model Missing", 0.0, viewer_filename

        model = joblib.load(MODEL_PATH)
        prediction = int(model.predict(feature_vector)[0])
        probs = model.predict_proba(feature_vector)[0]

        label = "Parkinson's Disease" if prediction == 1 else "Healthy Control"
        confidence = round(float(probs[prediction]) * 100, 2)
        
        return label, confidence, viewer_filename

    except Exception as e:
        print(f"❌ Eroare ML Logic: {e}")
        return "Analysis Error", 0.0, None