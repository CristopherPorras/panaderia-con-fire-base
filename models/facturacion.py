# === IMPORTACIONES GENERALES ===
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
from flask import session
from models import db

# === FUNCIÓN: Guardar una factura ===
def guardar_factura(form_data):
    #  Obtener el número de factura más alto y sumarle 1
    facturas_ref = db.collection('facturas').order_by(
        'numero_factura', direction=firestore.Query.DESCENDING
    ).limit(1).stream()

    numero_factura = 1
    for factura in facturas_ref:
        numero_factura = factura.to_dict().get('numero_factura', 0) + 1
        break  # Solo necesitamos el primero

    total = 0
    detalles = []

    #  Recorremos productos y calculamos subtotales
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

    #  Imprimimos el ID del vendedor logueado para verificar que está bien
    print("ID del vendedor en sesión:", session.get('user_id'))

    #  Creamos la factura con todos los datos
    factura_data = {
        'numero_factura': numero_factura,
        'cliente_id': form_data['cliente_id'],
        'fecha': datetime.now().strftime('%Y-%m-%d'),
        'total': int(total),
        'detalles': detalles,
        'vendedor_id': session.get('user_id', 'desconocido')  # ✅ Guardamos el ID del vendedor logueado
    }

    #  Guardamos la factura en Firebase
    db.collection('facturas').add(factura_data)
    print("📦 Factura guardada con vendedor_id:", factura_data['vendedor_id'])



# === FUNCIÓN: Obtener el próximo número de factura ===
def obtener_numero_factura():
    facturas = db.collection('facturas').order_by('fecha', direction=firestore.Query.DESCENDING).limit(1).stream()
    ultima = next(facturas, None)
    if ultima:
        num = ultima.to_dict().get("numero_factura", "0")
        return str(int(num) + 1)
    else:
        return "1"


# === FUNCIÓN: Buscar productos por texto ===
def buscar_productos(query):
    productos_ref = db.collection('productos')
    productos_docs = productos_ref.stream()
    resultados = []
    for doc in productos_docs:
        data = doc.to_dict()
        if query.lower() in data.get("nombre", "").lower():
            resultados.append({"id": doc.id, **data})
    return resultados


# === FUNCIÓN: Obtener facturas filtradas por texto o fecha ===
def obtener_facturas_filtradas(query='', fecha=''):
    facturas_ref = db.collection('facturas')
    facturas_docs = facturas_ref.stream()
    resultados = []

    for doc in facturas_docs:
        data = doc.to_dict()

        #  Obtener cliente
        cliente_id = data.get("cliente_id")
        cliente_ref = db.collection('clientes').document(cliente_id).get()
        cliente_data = cliente_ref.to_dict() if cliente_ref.exists else {"nombre": "Desconocido"}

        #  Obtener vendedor
        vendedor_id = data.get("vendedor_id")
        vendedor_ref = db.collection('vendedores').document(vendedor_id).get()
        vendedor_data = vendedor_ref.to_dict() if vendedor_ref.exists else {"nombre": "Desconocido"}

        #  Formatear la fecha
        factura_fecha = data.get("fecha")
        if factura_fecha:
            try:
                factura_fecha = factura_fecha.date()
            except:
                factura_fecha = datetime.strptime(factura_fecha, "%Y-%m-%d").date()
        else:
            factura_fecha = None

        #  Filtros
        cumple_busqueda = query.lower() in str(doc.id).lower() or query.lower() in cliente_data.get("nombre", "").lower()
        cumple_fecha = not fecha or (factura_fecha and factura_fecha.strftime("%Y-%m-%d") == fecha)

        #  Agregar si cumple filtros
        if cumple_busqueda and cumple_fecha:
            resultados.append({
                "id": doc.id,
                "numero": data.get("numero_factura"),
                "fecha": factura_fecha or datetime.now().date(),
                "cliente": {"nombre": cliente_data.get("nombre", "Desconocido")},
                "vendedor": {"nombre": vendedor_data.get("nombre", "Desconocido")},
                "detalles": data.get("detalles", []),
                "total": data.get("total", 0),
            })

    return resultados


# === FUNCIÓN: Eliminar factura por ID ===
def eliminar_factura_por_id(factura_id):
    db.collection('facturas').document(factura_id).delete()


# === FUNCIÓN: Obtener una factura por ID ===
def obtener_factura_por_id(factura_id):
    doc = db.collection('facturas').document(factura_id).get()
    if doc.exists:
        return doc.to_dict()
    return None


# === FUNCIÓN: Obtener el cliente a partir de una factura ===
def obtener_cliente_por_factura(factura):
    cliente_id = factura.get("cliente_id")
    if not cliente_id:
        return {}
    doc = db.collection('clientes').document(cliente_id).get()
    return doc.to_dict() if doc.exists else {}


# === FUNCIÓN: Obtener los detalles de una factura ===
def obtener_detalles_por_factura(factura_id):
    factura = obtener_factura_por_id(factura_id)
    if not factura:
        return []

    detalles = []
    for item in factura.get('detalles', []):
        producto_id = item.get('producto_id')
        producto_doc = db.collection('productos').document(producto_id).get()
        producto_data = producto_doc.to_dict() if producto_doc.exists else {}

        detalles.append({
            'nombre': producto_data.get('descripcion', 'Desconocido'),
            'cantidad': item.get('cantidad', 0),
            'precio_unitario': producto_data.get('valor_unitario', 0),
            'subtotal': item.get('cantidad', 0) * producto_data.get('valor_unitario', 0)
        })

    return detalles


# === FUNCIÓN: Calcular el total de ventas del día actual ===
def obtener_total_ventas_hoy():
    hoy = datetime.today().strftime('%Y-%m-%d')
    facturas_ref = db.collection('facturas')
    facturas_docs = facturas_ref.where('fecha', '==', hoy).stream()

    total_ventas = 0
    for factura in facturas_docs:
        datos = factura.to_dict()
        total = datos.get('total', 0)
        try:
            total_ventas += float(total)
        except ValueError:
            pass  # Si el valor no es numérico, lo ignoramos

    return total_ventas
