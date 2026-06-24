import os
import shutil
import tempfile
import dicom2nifti
import nibabel as nib
import pydicom
from pathlib import Path

def process_dicom_directory(source_dir, output_folder):
    """
    1. Scanează recursiv după foldere care conțin fișiere .dcm.
    2. Convertește seria DICOM în NIfTI.
    3. Extrage volumul 10 (dacă e 4D) pentru vizualizator.
    """
    
    if not os.path.exists(source_dir):
        print(f" Eroare: Nu am găsit folderul sursă: {source_dir}")
        return
    if not os.path.exists(output_folder):
        os.makedirs(output_folder, exist_ok=True)

    print(f"🔍 Scanez structura DICOM în: {source_dir}")
    print(f"📂 Fișierele convertite vor merge în: {output_folder}\n")

    processed_folders = 0
    
    for root, dirs, files in os.walk(source_dir):

        dicom_files = [f for f in files if f.endswith('.dcm')]
        
        if dicom_files:
            try:
                first_dcm_path = os.path.join(root, dicom_files[0])
                ds = pydicom.dcmread(first_dcm_path, stop_before_pixels=True)
                
                patient_id = str(ds.get("PatientID", "UnknownID")).replace(" ", "")
                protocol_name = str(ds.get("ProtocolName", "UnknownProto")).replace(" ", "_").replace("/", "-")
                
                if "rest" not in protocol_name.lower() and "fmri" not in protocol_name.lower():
                    continue 

                print(f"🔄 Convertesc: Pacient [{patient_id}] - Protocol [{protocol_name}]...")

                with tempfile.TemporaryDirectory() as temp_dir:
                    try:
                        dicom2nifti.convert_directory(root, temp_dir, compression=True, reorient=True)
                        
                        generated_files = [f for f in os.listdir(temp_dir) if f.endswith('.nii.gz')]
                        
                        if not generated_files:
                            print(f"⚠️  Conversia a eșuat (niciun nifti generat) pentru: {root}")
                            continue

                        temp_nifti_path = os.path.join(temp_dir, generated_files[0])
                        
                        img = nib.load(temp_nifti_path)
                        
                        final_filename = f"{patient_id}_{protocol_name}_viewer.nii.gz"
                        final_path = os.path.join(output_folder, final_filename)

                        if len(img.shape) == 4:
                            idx = min(10, img.shape[3] - 1)
                            data = img.get_fdata()
                            snapshot_data = data[..., idx]
                            
                            viewer_img = nib.Nifti1Image(snapshot_data, img.affine)
                            nib.save(viewer_img, final_path)
                            print(f" [4D->3D] Salvat: {final_filename}")
                        else:
                            shutil.copy(temp_nifti_path, final_path)
                            print(f"[3D Copy] Salvat: {final_filename}")

                        processed_folders += 1

                    except Exception as conv_err:
                        pass

            except Exception as e:
                print(f"⚠️ Eroare la folderul {root}: {e}")

    print(f"\n✨ Finalizat! Am convertit și procesat {processed_folders} serii DICOM.")


    SOURCE_DICOM = "/Users/ruthciuclea/Desktop/licenta/test_batch"

    DESTINATION = "/Users/ruthciuclea/Desktop/licenta/research_data/PD"
    
    process_dicom_directory(SOURCE_DICOM, DESTINATION)