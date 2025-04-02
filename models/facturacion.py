import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
from models.productos import db

db = firestore.client()

def guardar_factura(form_data):
    detalles = []
    for producto_id, cantidad in zip(form_data.getlist('producto_id'), form_data.getlist('cantidad')):
        detalles.append({
            'producto_id': producto_id,
            'cantidad': int(cantidad)
        })

    factura_data = {
        'numero_factura': form_data.get('numero_factura'),
        'fecha': datetime.now(),
        'cliente_id': form_data.get('cliente_id'),
        'detalles': detalles,
        'total': float(form_data.get('total'))
    }

    db.collection('facturas').add(factura_data)

def obtener_numero_factura():
    facturas = db.collection('facturas').order_by('fecha', direction=firestore.Query.DESCENDING).limit(1).stream()
    ultima = next(facturas, None)
    if ultima:
        num = ultima.to_dict().get("numero_factura", "0")
        return str(int(num) + 1)
    else:
        return "1"

def buscar_productos(query):
    productos_ref = db.collection('productos')
    productos_docs = productos_ref.stream()
    resultados = []
    for doc in productos_docs:
        data = doc.to_dict()
        if query.lower() in data.get("nombre", "").lower():
            resultados.append({"id": doc.id, **data})
    return resultados

def obtener_facturas_filtradas(query='', fecha=''):
    facturas_ref = db.collection('facturas')
    facturas_docs = facturas_ref.stream()

    resultados = []

    for doc in facturas_docs:
        data = doc.to_dict()
        cliente_id = data.get("cliente_id")
        cliente_ref = db.collection('clientes').document(cliente_id).get()
        cliente_data = cliente_ref.to_dict() if cliente_ref.exists else {"nombre": "Desconocido"}

        factura_fecha = data.get("fecha")
        if factura_fecha:
            try:
                factura_fecha = factura_fecha.date()
            except:
                factura_fecha = datetime.strptime(factura_fecha, "%Y-%m-%d").date()
        else:
            factura_fecha = None

        cumple_busqueda = query.lower() in str(doc.id).lower() or query.lower() in cliente_data.get("nombre", "").lower()
        cumple_fecha = not fecha or (factura_fecha and factura_fecha.strftime("%Y-%m-%d") == fecha)

        if cumple_busqueda and cumple_fecha:
            resultados.append({
                "numero": data.get("numero_factura"),
                "fecha": factura_fecha or datetime.now().date(),
                "cliente": {"nombre": cliente_data.get("nombre", "Desconocido")},
                "detalles": data.get("detalles", []),
                "total": data.get("total", 0)
            })

    return resultados
