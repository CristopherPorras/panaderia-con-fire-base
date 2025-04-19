from datetime import datetime
from flask import session
from google.cloud.firestore import Query
from extensions import db

# === FUNCIÓN: Obtener el próximo número de factura ===
def obtener_numero_factura():
    facturas_ref = (
        db.collection('facturas')
        .order_by('numero_factura', direction=Query.DESCENDING)
        .limit(1)
        .stream()
    )
    primera = next(facturas_ref, None)
    return (primera.to_dict().get('numero_factura', 0) + 1) if primera else 1

# === FUNCIÓN: Guardar una factura ===
def guardar_factura(form_data):
    numero_factura = obtener_numero_factura()

    total = 0
    detalles = []

    productos_ids = form_data.getlist('producto_id')
    cantidades = form_data.getlist('cantidad')
    for producto_id, cantidad in zip(productos_ids, cantidades):
        producto_doc = db.collection('productos').document(producto_id).get()
        if not producto_doc.exists:
            continue
        data = producto_doc.to_dict()
        cantidad_int = int(cantidad)
        precio_unitario = float(data.get('valor_unitario', 0))
        subtotal = cantidad_int * precio_unitario
        total += subtotal

        detalles.append({
            'producto_id': producto_id,
            'nombre': data.get('descripcion', 'Desconocido'),
            'precio_unitario': int(precio_unitario),
            'cantidad': cantidad_int,
            'subtotal': subtotal
        })

    metodo_pago = form_data.get('metodo_pago', 'efectivo')  # ← Asegura que se obtenga el valor
    efectivo_recibido = float(form_data.get('efectivo_recibido') or 0)

    factura_data = {
        'numero_factura': numero_factura,
        'cliente_id': form_data['cliente_id'],
        'fecha': datetime.now(),  #  Se guarda como datetime real (timestamp)
        'total': int(total),
        'detalles': detalles,
        'vendedor_id': session.get('user_id', 'desconocido'),
        'metodo_pago': metodo_pago,
        'efectivo_recibido': efectivo_recibido if metodo_pago == 'efectivo' else 0
    }

    db.collection('facturas').add(factura_data)
    print("📦 Factura guardada con:", factura_data)


# === FUNCIÓN: Obtener total ventas del día ===
def obtener_total_ventas_hoy():
    hoy = datetime.now().strftime('%Y-%m-%d')
    docs = db.collection('facturas').where('fecha', '>=', hoy).stream()
    return sum(doc.to_dict().get('total', 0) for doc in docs)

from datetime import datetime
from extensions import db

# === FUNCIÓN: Obtener facturas con filtros ===
def obtener_facturas_filtradas(query='', fecha=''):
    facturas_ref = db.collection('facturas')
    todas_facturas = facturas_ref.stream()

    facturas_filtradas = []
    fecha_consulta = datetime.strptime(fecha, '%Y-%m-%d').date() if fecha else datetime.today().date()

    for doc in todas_facturas:
        data = doc.to_dict()
        data['id'] = doc.id
        data['numero'] = data.get('numero_factura', 0)

        # 🕒 Obtenemos la fecha y la convertimos a tipo date
        fecha_guardada = data.get('fecha')
        if isinstance(fecha_guardada, str):
            try:
                fecha_factura = datetime.strptime(fecha_guardada, '%Y-%m-%d %H:%M:%S').date()
            except:
                try:
                    fecha_factura = datetime.strptime(fecha_guardada, '%Y-%m-%d').date()
                except:
                    continue
        elif isinstance(fecha_guardada, datetime):
            fecha_factura = fecha_guardada.date()
        else:
            continue

        # Filtro por fecha exacta
        if fecha_factura != fecha_consulta:
            continue

        # Filtro por texto (nombre del cliente o número de factura)
        cliente_doc = db.collection('clientes').document(data.get('cliente_id', '')).get()
        cliente_nombre = cliente_doc.to_dict().get('nombre', '') if cliente_doc.exists else ''
        if query and query.lower() not in cliente_nombre.lower() and query not in str(data['numero']):
            continue

        data['cliente'] = {'nombre': cliente_nombre}
        data['fecha'] = fecha_factura.strftime('%d/%m/%Y')

        # Vendedor
        vendedor_id = data.get('vendedor_id')
        if vendedor_id:
            vendedor_doc = db.collection('vendedores').document(vendedor_id).get()
            if vendedor_doc.exists:
                data['vendedor'] = vendedor_doc.to_dict()

        facturas_filtradas.append(data)

    # Ordenamos las facturas de mayor a menor por número
    facturas_ordenadas = sorted(facturas_filtradas, key=lambda x: x['numero'], reverse=True)

    return facturas_ordenadas


# === FUNCIÓN: Eliminar factura por ID ===
def eliminar_factura_por_id(factura_id):
    db.collection('facturas').document(factura_id).delete()

# === FUNCIÓN: Obtener factura por ID ===
def obtener_factura_por_id(factura_id):
    ref = db.collection('facturas').document(factura_id).get()
    if ref.exists:
        return ref.to_dict()
    return {}

# === FUNCIÓN: Obtener cliente desde una factura ===
def obtener_cliente_por_factura(factura):
    cliente_id = factura.get('cliente_id')
    if cliente_id:
        doc = db.collection('clientes').document(cliente_id).get()
        return doc.to_dict() if doc.exists else {'nombre': 'Desconocido'}
    return {'nombre': 'Desconocido'}

# === FUNCIÓN: Obtener detalles desde factura ===
def obtener_detalles_por_factura(factura_id):
    ref = db.collection('facturas').document(factura_id).get()
    if not ref.exists:
        return []

    factura = ref.to_dict()
    detalles_finales = []
    for item in factura.get('detalles', []):
        p = db.collection('productos').document(item.get('producto_id')).get()
        pd = p.to_dict() if p.exists else {}
        detalles_finales.append({
            'nombre': pd.get('descripcion', 'Desconocido'),
            'cantidad': item.get('cantidad', 0),
            'precio_unitario': pd.get('valor_unitario', 0),
            'subtotal': item.get('cantidad', 0) * pd.get('valor_unitario', 0)
        })
    return detalles_finales
