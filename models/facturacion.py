from datetime import datetime
from flask import session
from google.cloud.firestore import Query
from extensions import db  # Usamos el cliente Firestore inicializado en extensions.py

# === FUNCIÓN: Guardar una factura ===
def guardar_factura(form_data):
    """
    Guarda una factura nueva en Firestore.
    Calcula el próximo número de factura y el total según los detalles.
    """
    # Obtenemos la factura con mayor número y le sumamos 1
    facturas_ref = (
        db.collection('facturas')
          .order_by('numero_factura', direction=Query.DESCENDING)
          .limit(1)
          .stream()
    )
    numero_factura = 1
    primera = next(facturas_ref, None)
    if primera:
        numero_factura = primera.to_dict().get('numero_factura', 0) + 1

    total = 0
    detalles = []

    # Recorremos cada producto seleccionado y calculamos subtotal
    productos_ids = form_data.getlist('producto_id')
    cantidades    = form_data.getlist('cantidad')
    for producto_id, cantidad in zip(productos_ids, cantidades):
        producto_doc = db.collection('productos').document(producto_id).get()
        if not producto_doc.exists:
            continue
        data = producto_doc.to_dict()
        cantidad_int     = int(cantidad)
        precio_unitario  = float(data.get('valor_unitario', 0))
        subtotal         = cantidad_int * precio_unitario
        total           += subtotal

        detalles.append({
            'producto_id':    producto_id,
            'nombre':         data.get('descripcion', 'Desconocido'),
            'precio_unitario': int(precio_unitario),
            'cantidad':       cantidad_int,
            'subtotal':       subtotal
        })

    # Mostramos el ID del vendedor en sesión para depuración
    print("ID del vendedor en sesión:", session.get('user_id'))

    # Creamos el diccionario de la factura
    factura_data = {
        'numero_factura': numero_factura,
        'cliente_id':     form_data['cliente_id'],
        'fecha':          datetime.now().strftime('%Y-%m-%d'),
        'total':          int(total),
        'detalles':       detalles,
        'vendedor_id':    session.get('user_id', 'desconocido')
    }

    # Guardamos en Firestore
    db.collection('facturas').add(factura_data)
    print("📦 Factura guardada con vendedor_id:", factura_data['vendedor_id'])


# === FUNCIÓN: Obtener el próximo número de factura ===
def obtener_numero_factura():
    """
    Retorna el siguiente número de factura como string.
    """
    facturas = (
        db.collection('facturas')
          .order_by('fecha', direction=Query.DESCENDING)
          .limit(1)
          .stream()
    )
    ultima = next(facturas, None)
    if ultima:
        num = ultima.to_dict().get('numero_factura', 0)
        return str(int(num) + 1)
    return "1"


# === FUNCIÓN: Buscar productos por texto ===
def buscar_productos(query):
    """
    Retorna lista de productos cuyo nombre contiene la query.
    """
    productos_docs = db.collection('productos').stream()
    resultados = []
    for doc in productos_docs:
        data = doc.to_dict()
        nombre = data.get('nombre', '').lower()
        if query.lower() in nombre:
            resultados.append({"id": doc.id, **data})
    return resultados


# === FUNCIÓN: Obtener facturas filtradas por texto o fecha ===
def obtener_facturas_filtradas(query='', fecha=''):
    """
    Retorna facturas que coinciden con búsqueda en ID o nombre de cliente,
    y/o con la fecha exacta.
    """
    facturas_docs = db.collection('facturas').stream()
    resultados = []

    for doc in facturas_docs:
        data = doc.to_dict()

        # Obtenemos datos del cliente
        cliente_id   = data.get("cliente_id")
        cliente_doc  = db.collection('clientes').document(cliente_id).get()
        cliente_data = cliente_doc.to_dict() if cliente_doc.exists else {"nombre": "Desconocido"}

        # Obtenemos datos del vendedor
        vendedor_id   = data.get("vendedor_id")
        vendedor_doc  = db.collection('vendedores').document(vendedor_id).get()
        vendedor_data = vendedor_doc.to_dict() if vendedor_doc.exists else {"nombre": "Desconocido"}

        # Parseamos la fecha
        fecha_str = data.get("fecha")
        if fecha_str:
            try:
                fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            except:
                fecha_obj = datetime.today().date()
        else:
            fecha_obj = None

        # Comprobamos filtros
        texto_id     = query.lower() in str(doc.id).lower()
        texto_nombre = query.lower() in cliente_data.get("nombre", "").lower()
        cumple_busqueda = not query or (texto_id or texto_nombre)
        cumple_fecha    = not fecha or (fecha_obj and fecha_obj.strftime("%Y-%m-%d") == fecha)

        if cumple_busqueda and cumple_fecha:
            resultados.append({
                "id":       doc.id,
                "numero":   data.get("numero_factura"),
                "fecha":    fecha_obj or datetime.today().date(),
                "cliente":  {"nombre": cliente_data.get("nombre")},
                "vendedor": {"nombre": vendedor_data.get("nombre")},
                "detalles": data.get("detalles", []),
                "total":    data.get("total", 0)
            })

    return resultados


# === FUNCIÓN: Eliminar factura por ID ===
def eliminar_factura_por_id(factura_id):
    """
    Elimina la factura indicada de Firestore.
    """
    db.collection('facturas').document(factura_id).delete()


# === FUNCIÓN: Obtener una factura por ID ===
def obtener_factura_por_id(factura_id):
    """
    Retorna el diccionario de la factura o None si no existe.
    """
    doc = db.collection('facturas').document(factura_id).get()
    return doc.to_dict() if doc.exists else None


# === FUNCIÓN: Obtener cliente a partir de una factura ===
def obtener_cliente_por_factura(factura):
    """
    Dado el diccionario de factura, retorna datos del cliente.
    """
    cliente_id = factura.get("cliente_id")
    if not cliente_id:
        return {}
    doc = db.collection('clientes').document(cliente_id).get()
    return doc.to_dict() if doc.exists else {}


# === FUNCIÓN: Obtener detalles de una factura ===
def obtener_detalles_por_factura(factura_id):
    """
    Retorna la lista de detalles con nombre, cantidad y subtotales.
    """
    factura = obtener_factura_por_id(factura_id)
    if not factura:
        return []

    detalles = []
    for item in factura.get('detalles', []):
        producto_doc = db.collection('productos').document(item.get('producto_id')).get()
        producto_data = producto_doc.to_dict() if producto_doc.exists else {}
        detalles.append({
            'nombre':          producto_data.get('descripcion', 'Desconocido'),
            'cantidad':        item.get('cantidad', 0),
            'precio_unitario': producto_data.get('valor_unitario', 0),
            'subtotal':        item.get('cantidad', 0) * producto_data.get('valor_unitario', 0)
        })
    return detalles


# === FUNCIÓN: Calcular el total de ventas del día ===
def obtener_total_ventas_hoy():
    """
    Suma los totales de facturas cuya fecha es hoy.
    """
    hoy_str = datetime.today().strftime('%Y-%m-%d')
    facturas_docs = db.collection('facturas').where('fecha', '==', hoy_str).stream()

    total_ventas = 0
    for factura in facturas_docs:
        datos = factura.to_dict()
        total  = datos.get('total', 0)
        try:
            total_ventas += float(total)
        except ValueError:
            continue

    return total_ventas
