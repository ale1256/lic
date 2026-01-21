import os
import matplotlib
# Setam backend-ul Matplotlib pe 'Agg' pentru a preveni erorile pe Mac
matplotlib.use('Agg') 

def analyze_fmri(file_path):
    """
    Functia principala de analiza.
    Returneaza: (Eticheta, Confidenta, Calea catre fisierul 3D pentru viewer)
    """
    
    # --- 1. Importuri Lazy (Se incarca doar cand apesi butonul) ---
    import numpy as np
    import joblib
    import nibabel as nib
    from nilearn import datasets, maskers, connectome
    import warnings
    
    warnings.filterwarnings("ignore")

    # --- 2. Configurare Cai ---
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    MODEL_PATH = os.path.join(BASE_DIR, 'diagnosis', 'ml_models', 'pd_classifier.pkl')
    
    # Definim calea pentru fisierul "usor" (3D) destinat viewer-ului web
    viewer_path = file_path.replace('.nii.gz', '_viewer.nii.gz')
    
    print(f"🧠 [ML Logic] Incepe procesarea pentru: {os.path.basename(file_path)}")

    try:
        # --- 3. Optimizare Viewer (Conversie 4D -> 3D) ---
        img = nib.load(file_path)
        
        # Daca nu am creat deja fisierul mic, il cream acum
        if not os.path.exists(viewer_path):
            print("   -> Generare snapshot 3D pentru vizualizare rapida...")
            # Daca imaginea are 4 dimensiuni (timp), luam doar primul volum
            if len(img.shape) == 4:
                first_volume = img.slicer[..., 0]
                nib.save(first_volume, viewer_path)
            else:
                # Daca e deja 3D, il copiem ca atare
                nib.save(img, viewer_path)
        
        # --- 4. Procesare Neurostiintifica (Nilearn) ---
        
        print("   -> Incarcare atlas MSDL...")
        atlas = datasets.fetch_atlas_msdl()

        # Configuram extractorul de semnal
        masker = maskers.NiftiMapsMasker(
            maps_img=atlas.maps, 
            standardize=True,      
            memory='nilearn_cache', 
            verbose=0
        )

        # Extragem seriile de timp
        print("   -> Extragere serii de timp din datele fMRI...")
        time_series = masker.fit_transform(img)
        print(f"   -> Semnal extras. Dimensiuni: {time_series.shape}")
        
        # --- 5. Calcule Matematice (Conectivitate) ---

        # Calculam matricea de corelatie
        correlation_measure = connectome.ConnectivityMeasure(kind='correlation')
        correlation_matrix = correlation_measure.fit_transform([time_series])[0]
        
        # Aplatizam matricea intr-un singur vector de features (741 valori)
        mask = np.tril(np.ones(correlation_matrix.shape), k=-1).astype(bool)
        feature_vector = correlation_matrix[mask].reshape(1, -1)
        
        # --- 6. Predictie ML (SVM) ---
        
        if not os.path.exists(MODEL_PATH):
            print(f"❌ Model negasit la: {MODEL_PATH}")
            # Returnam viewer_path chiar daca nu merge ML-ul
            return "Model Missing", 0.0, viewer_path
            
        model = joblib.load(MODEL_PATH)
        
        prediction_class = model.predict(feature_vector)[0]
        probabilities = model.predict_proba(feature_vector)[0]

        if prediction_class == 1:
            final_label = "Parkinson's Disease"
            final_conf = round(probabilities[1] * 100, 2)
        else:
            final_label = "Healthy Control"
            final_conf = round(probabilities[0] * 100, 2)

        print(f"✅ Rezultat final: {final_label} ({final_conf}%)")
        
        # RETURNAM 3 VALORI
        return final_label, final_conf, viewer_path

    except Exception as e:
        print(f"❌ Eroare critica in analiza: {e}")
        return "Analysis Failed", 0.0, None