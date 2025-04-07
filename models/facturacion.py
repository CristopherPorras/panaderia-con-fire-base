import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
from models.productos import db

db = firestore.client()

from datetime import datetime
from firebase_admin import firestore

def guardar_factura(form_data):
    # Obtener el número de factura más alto y sumarle 1
    facturas_ref = db.collection('facturas').order_by('numero_factura', direction=firestore.Query.DESCENDING).limit(1).stream()
    numero_factura = 1
    for factura in facturas_ref:
        numero_factura = factura.to_dict().get('numero_factura', 0) + 1
        break  # Solo necesitamos la primera

    total = 0
    detalles = []
    for producto_id, cantidad in zip(form_data.getlist('producto_id'), form_data.getlist('cantidad')):
        producto_ref = db.collection('productos').document(producto_id).get()
        if producto_ref.exists:
            producto_data = producto_ref.to_dict()
            cantidad_int = int(cantidad)
            precio_unitario = float(producto_data.get('valor_unitario', 0))
            subtotal = cantidad_int * precio_unitario
            total += subtotal

            detalles.append({
                'producto_id': producto_id,
                'nombre': producto_data.get('descripcion', 'Desconocido'),
                'precio_unitario': int(precio_unitario),
                'cantidad': cantidad_int,
                'subtotal': subtotal
            })

    factura_data = {
        'numero_factura': numero_factura,
        'cliente_id': form_data['cliente_id'],  # Asegúrate de que el campo <input name="nombre"> esté en el formulario
        'fecha': datetime.now().strftime('%Y-%m-%d'),
        'total': int(total),
        'detalles': detalles
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
                "id": doc.id,
                "numero": data.get("numero_factura"),
                "fecha": factura_fecha or datetime.now().date(),
                "cliente": {"nombre": cliente_data.get("nombre", "Desconocido")},
                "detalles": data.get("detalles", []),
                "total": data.get("total", 0),
            })

    return resultados

def eliminar_factura_por_id(factura_id):
    db.collection('facturas').document(factura_id).delete()
