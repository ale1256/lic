import nibabel as nib
from nilearn.image import resample_img
import numpy as np

# Numele fișierului tău gigant
input_file = "/Users/ruthciuclea/Desktop/licenta/media/scans/test_control_HC_4D_8mwBLlU_Zv1JeQA_1GN31NQ_Uhegdu6_j2rqkvW.nii.gz"
output_file = "fisier_mic_optimizat.nii.gz"

print("Incarc fisierul gigant (asteapta putin)...")
img = nib.load(input_file)

# Il redimensionam la o rezolutie standard (ex: 4mm)
# Asta va reduce dimensiunea de la 1.5GB la probabil sub 100MB
print("Redimensionare...")
downsampled_img = resample_img(img, target_affine=np.eye(4)*4, interpolation='continuous')

print(f"Salvare in {output_file}...")
downsampled_img.to_filename(output_file)
print("Gata! Incearca sa incarci acest fisier nou in aplicatie.")