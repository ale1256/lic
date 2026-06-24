import os
import numpy as np
import joblib
import nibabel as nib
from nibabel.processing import resample_to_output
from nilearn import datasets, maskers, connectome, plotting
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter
import warnings

warnings.filterwarnings("ignore")

def generate_viewer_volume(source_path, viewer_path=None):
    """
    Generează un volum 3D optimizat pentru viewer.
    - Pentru 4D folosește mediana temporală.
    - Reesantionează la 2mm isotropic pentru afișare mai fină.
    - Aplică normalizare/contrast robust pentru lizibilitate.
    """
    if viewer_path is None:
        dir_name = os.path.dirname(source_path)
        base_name = os.path.basename(source_path)
        clean_name = base_name.replace(".nii.gz", "").replace(".nii", "").replace("_viewer", "")
        viewer_path = os.path.join(dir_name, f"{clean_name}_viewer.nii.gz")

    img = nib.as_closest_canonical(nib.load(source_path))
    data = img.get_fdata(dtype=np.float32)

    if len(img.shape) == 4:
        snapshot_data = np.nanmedian(data, axis=3)
    else:
        snapshot_data = data

    snapshot_data = np.nan_to_num(snapshot_data, nan=0.0, posinf=0.0, neginf=0.0)
    viewer_img = nib.Nifti1Image(snapshot_data.astype(np.float32), img.affine)

    voxel_sizes = viewer_img.header.get_zooms()[:3]
    if any(v > 2.2 for v in voxel_sizes):
        viewer_img = resample_to_output(viewer_img, voxel_sizes=(2.0, 2.0, 2.0), order=3)

    snapshot_data = viewer_img.get_fdata(dtype=np.float32)
    snapshot_data = np.nan_to_num(snapshot_data, nan=0.0, posinf=0.0, neginf=0.0)

    positive_voxels = snapshot_data[snapshot_data > 0]
    source_vals = positive_voxels if positive_voxels.size > 100 else snapshot_data.ravel()
    if source_vals.size > 0:
        p_low, p_high = np.percentile(source_vals, [1.0, 99.5])
        if p_high > p_low:
            snapshot_data = np.clip(snapshot_data, p_low, p_high)
            snapshot_data = (snapshot_data - p_low) / (p_high - p_low)
            snapshot_data = np.sqrt(snapshot_data)

    blur = gaussian_filter(snapshot_data, sigma=0.7)
    snapshot_data = np.clip(snapshot_data + 0.6 * (snapshot_data - blur), 0.0, 1.0)

    snapshot_data = snapshot_data.astype(np.float32)
    viewer_img = nib.Nifti1Image(snapshot_data, viewer_img.affine)
    viewer_img.header.set_data_dtype(np.float32)
    viewer_img.header["cal_min"] = float(np.min(snapshot_data))
    viewer_img.header["cal_max"] = float(np.max(snapshot_data))
    nib.save(viewer_img, viewer_path)

    return os.path.basename(viewer_path)

def analyze_fmri(file_path):
    """
    Extrage snapshot 3D, generează Matricea de Conectivitate .png
    și prezice stadiul de severitate.
    """
    dir_name = os.path.dirname(file_path)
    base_name = os.path.basename(file_path)
    
    clean_name = base_name.replace('.nii.gz', '').replace('.nii', '').replace('_viewer', '')
    
    viewer_filename = f"{clean_name}_viewer.nii.gz"
    viewer_path = os.path.join(dir_name, viewer_filename)
    
    matrix_filename = f"{clean_name}_matrix.png"
    matrix_path = os.path.join(dir_name, matrix_filename)

    try:
        generate_viewer_volume(file_path, viewer_path)

        try:
            img = nib.load(file_path)
            if len(img.shape) < 4 or (len(img.shape) >= 4 and img.shape[3] < 2):
                return "Unsupported Modality", 0.0, viewer_filename, "N/A", None
        except Exception:
            return "Analysis Error", 0.0, viewer_filename, "Error", None

        atlas = datasets.fetch_atlas_msdl()
        masker = maskers.NiftiMapsMasker(
            maps_img=atlas.maps, 
            standardize='zscore_sample',
            detrend=True,
            resampling_target='maps',
            verbose=0
        )
        
        time_series = masker.fit_transform(file_path)
        
        correlation_measure = connectome.ConnectivityMeasure(kind='correlation')
        correlation_matrix = correlation_measure.fit_transform([time_series])[0]
        
        plt.figure(figsize=(10, 8))
        plotting.plot_matrix(
            correlation_matrix, 
            labels=atlas.labels, 
            colorbar=True,
            vmax=0.8, 
            vmin=-0.8,
            title="Functional Connectivity Matrix (ROI-to-ROI)"
        )
        plt.savefig(matrix_path)
        plt.close()

        conn_vectorizer = connectome.ConnectivityMeasure(kind='correlation', vectorize=True, discard_diagonal=True)
        feature_vector = conn_vectorizer.fit_transform([time_series])

        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        MODEL_PATH = os.path.join(BASE_DIR, 'diagnosis', 'ml_models', 'pd_classifier.pkl')
        
        if not os.path.exists(MODEL_PATH):
            return "Model Missing", 0.0, viewer_filename, "N/A", None

        model = joblib.load(MODEL_PATH)
        prediction = int(model.predict(feature_vector)[0])
        probs = model.predict_proba(feature_vector)[0]

        label = "Parkinson's Disease" if prediction == 1 else "Healthy Control"
        confidence = round(float(probs[prediction]) * 100, 2)

        stage = "N/A"
        if label == "Parkinson's Disease":
            if confidence < 60:
                stage = "Stage 1 (Unilateral)"
            elif confidence < 75:
                stage = "Stage 2 (Bilateral, no balance impairment)"
            elif confidence < 85:
                stage = "Stage 3 (Mild to moderate disability)"
            elif confidence < 95:
                stage = "Stage 4 (Severe disability)"
            else:
                stage = "Stage 5 (Wheelchair bound or bedridden)"
        else:
            stage = "Normal"
        return label, confidence, viewer_filename, stage, matrix_filename

    except Exception as e:
        print(f" Eroare ML Logic: {e}")
        return "Analysis Error", 0.0, viewer_filename, "Error", None
