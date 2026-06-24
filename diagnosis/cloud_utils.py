import os
import uuid
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

app_id = "neurodetect-ppmi-2025"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_PATH = os.path.join(BASE_DIR, 'serviceAccountKey.json')

db = None

def get_firestore_client():
    """
    Inițializează conexiunea securizată cu Cloud Firestore.
    """
    global db
    if db is None:
        try:
            if os.path.exists(CERT_PATH):
                if not firebase_admin._apps:
                    cred = credentials.Certificate(CERT_PATH)
                    firebase_admin.initialize_app(cred)
                db = firestore.client()
                print("📡 Conexiune stabilită cu succes prin serviceAccountKey.json")
            else:
                if not firebase_admin._apps:
                    firebase_admin.initialize_app()
                db = firestore.client()
        except Exception as e:
            print(f"⚠️ Eroare inițializare Firebase: {e}")
            return None
    return db

def save_scan_to_cloud(user_id, scan_data):
    """
    Salvează rezultatul unui diagnostic în Firestore.
    Calea: /artifacts/{appId}/public/data/scans
    """
    client = get_firestore_client()
    if client is None:
        print("📴 Cloud Offline: Verificați prezența fișierului serviceAccountKey.json")
        return None

    try:

        doc_id = str(uuid.uuid4())
        
        doc_ref = client.collection('artifacts').document(app_id).collection('public').document('data').collection('scans').document(doc_id)
        
        full_data = {
            **scan_data,
            'cloud_id': doc_id,
            'user_id': str(user_id),
            'timestamp': datetime.now().isoformat(),
            'status': 'finalized'
        }
        
        doc_ref.set(full_data)
        print(f"[Cloud Sync] Datele pacientului {scan_data.get('patient_id')} au fost sincronizate.")
        return doc_id
    except Exception as e:
        print(f" Eroare la scrierea în Cloud: {e}")
        return None