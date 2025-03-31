from firebase_admin import firestore
from models.productos import db


def registrar_factura(datos_factura):
    """Registra una nueva factura en Firestore."""
    try:
        facturas_ref = db.collection('facturas')
        nueva_factura = facturas_ref.document()  # Crea un nuevo documento con ID automático
        nueva_factura.set(datos_factura)  # Guarda la factura en Firestore
        return "Factura registrada correctamente."
    except Exception as e:
        return f"Error al registrar la factura: {str(e)}"

# Inicializa la conexión a Firestore (asegúrate de que Firebase ya esté inicializado en app.py)
db = firestore.client()

def obtener_numero_factura():
    """Obtiene el último número de factura y lo incrementa."""
    config_ref = db.collection("config").document("facturas")
    config_doc = config_ref.get()
    
    if config_doc.exists:
        numero_factura = config_doc.to_dict().get("ultimo_numero", 0) + 1
    else:
        numero_factura = 1
        config_ref.set({"ultimo_numero": 0})

    return numero_factura

def guardar_factura(data):
    """Guarda la factura en Firestore y actualiza el número de factura."""
    numero_factura = obtener_numero_factura()

    factura = {
        "numero_factura": numero_factura,
        "cliente_id": data.get('cliente_id'),
        "total": float(data.get('total', 0)),
    }

    facturas_ref = db.collection("facturas")
    facturas_ref.document(str(numero_factura)).set(factura)

    # Actualizar el último número de factura en Firestore
    config_ref = db.collection("config").document("facturas")
    config_ref.set({"ultimo_numero": numero_factura}, merge=True)

    return numero_factura  # Devolver el número generado

def buscar_productos(query):
    """Filtra productos por descripción en Firestore."""
    productos_ref = db.collection("productos")
    productos_docs = productos_ref.stream()

    productos_filtrados = []
    for doc in productos_docs:
        producto = doc.to_dict()
        if query.lower() in producto.get("descripcion", "").lower():
            productos_filtrados.append({
                "id": doc.id,
                "descripcion": producto.get("descripcion", ""),
                "valor_unitario": producto.get("valor_unitario", 0)
            })

    return productos_filtrados  # Devuelve los productos filtrados

