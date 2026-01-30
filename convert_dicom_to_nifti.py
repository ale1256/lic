import os
import subprocess

def convert_dicom_to_nifti(source_dir, output_dir):
    """
    Converteste toate fisierele DICOM dintr-un folder intr-un singur fisier NIfTI.
    Necesita dcm2niix instalat (conda install -c conda-forge dcm2niix).
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"🚀 Incepere conversie din: {source_dir}")
    
    # Rulam dcm2niix
    # -z y : comprima in .nii.gz
    # -f %f : pastreaza numele original al folderului/fisierului
    # -o : folderul de iesire
    try:
        command = [
            "dcm2niix",
            "-z", "y",
            "-f", "%f_%p",
            "-o", output_dir,
            source_dir
        ]
        subprocess.run(command, check=True)
        print(f"✅ Conversie finalizata! Fisierele .nii.gz sunt in: {output_dir}")
    except FileNotFoundError:
        print("❌ Eroare: dcm2niix nu este instalat.")
        print("Ruleaza: 'conda install -c conda-forge dcm2niix' sau 'brew install dcm2niix'")
    except Exception as e:
        print(f"❌ Eroare la conversie: {e}")

if __name__ == "__main__":
    # Calea ta de pe Mac
    INPUT_FOLDER = "/Users/ruthciuclea/Desktop/licenta/folder_wit_pd"
    # Unde vrei sa apara fisierele NIfTI gata de antrenat
    OUTPUT_FOLDER = "/Users/ruthciuclea/Desktop/licenta/nifti_ready"
    
    convert_dicom_to_nifti(INPUT_FOLDER, OUTPUT_FOLDER)