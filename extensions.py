import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

PDFSHIFT_API_KEY = None
db = None

def init_extensions(cred_filename='delicias.json'):
    global PDFSHIFT_API_KEY, db

    # --- PDFShift ---
    pdfshift_path = '/etc/secrets/pdfshift.json'
    if not os.path.exists(pdfshift_path):
        pdfshift_path = os.path.join(os.getcwd(), 'instance', 'pdfshift.json')
    with open(pdfshift_path, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
        PDFSHIFT_API_KEY = cfg.get('api_key')
        if not PDFSHIFT_API_KEY:
            raise RuntimeError("Falta 'api_key' en pdfshift.json")

    # --- Firebase ---
    cred_path = os.path.join(os.getcwd(), 'instance', cred_filename)
    if not os.path.exists(cred_path):
        raise RuntimeError(f"No se encontró credenciales de Firebase en {cred_path}")
    cred = credentials.Certificate(cred_path) 
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    db = firestore.client()
