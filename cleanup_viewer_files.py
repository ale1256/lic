import os
import glob

def sterge_fisiere_viewer():
    """
    Șterge toate fișierele care conțin 'viewer' în nume din folderul media/scans.
    Acest lucru rezolvă erorile 404 și ecranele negre din vizualizatorul 3D.
    """
    # Calea absolută către folderul tău de scanări pe Mac
    target_dir = "/Users/ruthciuclea/Desktop/licenta/media/scans"
    
    if not os.path.exists(target_dir):
        print(f"❌ Eroare: Folderul '{target_dir}' nu a fost găsit.")
        return

    # Căutăm orice fișier care are "viewer" în denumire
    pattern = os.path.join(target_dir, "*viewer*")
    fisiere = glob.glob(pattern)

    if not fisiere:
        print("✅ Nu am găsit fișiere 'viewer'. Folderul este deja curat.")
        return

    print(f"🧹 Am găsit {len(fisiere)} fișiere pentru ștergere. Se curăță...")

    count = 0
    for file_path in fisiere:
        try:
            os.remove(file_path)
            print(f"  🗑️ Șters: {os.path.basename(file_path)}")
            count += 1
        except Exception as e:
            print(f"  ❌ Nu am putut șterge {os.path.basename(file_path)}: {e}")

    print(f"\n✨ Finalizat! Au fost eliminate {count} fișiere.")
    print("🚀 Acum poți face un upload nou în aplicație.")

if __name__ == "__main__":
    sterge_fisiere_viewer()