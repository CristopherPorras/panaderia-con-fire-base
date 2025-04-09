import firebase_admin
from firebase_admin import credentials, firestore
import os

# Ruta al archivo de credenciales
ruta_credenciales = os.path.join(os.path.dirname(__file__), '..', 'instance', 'delicias.json')

# Inicializa Firebase solo si no está ya inicializado
if not firebase_admin._apps:
    cred = credentials.Certificate(ruta_credenciales)
    firebase_admin.initialize_app(cred)

# Cliente de Firestore, accesible como models.db
db = firestore.client()
