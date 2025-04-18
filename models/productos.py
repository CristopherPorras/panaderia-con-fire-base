import os
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from google.cloud.firestore import Query
from extensions import db  # Cliente Firestore inicializado en extensions.py

# === Función auxiliar: verifica extensión permitida ===
def allowed_file(filename, allowed_extensions):
    return (
        '.' in filename 
        and filename.rsplit('.', 1)[1].lower() in allowed_extensions
    )

# === FUNCIÓN: Mostrar lista de productos ===
def fun_productos():
    """
    Recupera productos de Firestore, aplica búsqueda y filtro por categoría,
    y renderiza la plantilla 'productos.html' con los datos.
    """
    productos_ref = db.collection('productos')

    # Búsqueda por descripción (igual que INDEX LIKE)
    query_text = request.args.get('query', '').strip()
    if query_text:
        productos_ref = (
            productos_ref
            .where('descripcion', '>=', query_text)
            .where('descripcion', '<=', query_text + '\uf8ff')
        )

    # Filtro por categoría
    categoria_id = request.args.get('categoria')
    if categoria_id:
        productos_ref = productos_ref.where('categoria_id', '==', categoria_id)

    # Obtenemos los documentos
    productos_docs = productos_ref.stream()
    lista_productos = []
    for doc in productos_docs:
        data = doc.to_dict()
        data['id'] = doc.id
        lista_productos.append(data)

    # Obtenemos todas las categorías para el filtro
    categorias_docs = db.collection('categorias').stream()
    lista_categorias = []
    for cat in categorias_docs:
        cd = cat.to_dict()
        cd['id'] = cat.id
        lista_categorias.append(cd)

    return render_template(
        'productos.html',
        productos=lista_productos,
        categorias=lista_categorias
    )

# === FUNCIÓN: Registrar un nuevo producto ===
def fun_regis_productos(form_data, file, upload_folder, allowed_extensions):
    """
    Crea un ID incremental guardado en 'config/counters',
    procesa la imagen si existe, y guarda el producto en Firestore.
    """
    # Paso 1: obtener/crear contador
    config_ref = db.collection('config').document('counters')
    config_doc = config_ref.get()
    if config_doc.exists:
        ultimo_id = config_doc.to_dict().get('ultimo_id', 0)
    else:
        ultimo_id = 0
    nuevo_id = ultimo_id + 1
    config_ref.set({'ultimo_id': nuevo_id}, merge=True)

    # Paso 2: datos del formulario
    descripcion     = form_data.get('descripcion', '').strip()
    valor_unitario  = float(form_data.get('valor_unitario', 0))
    unidad_medida   = form_data.get('unidad_medida', '').strip()
    cantidad_stock  = int(form_data.get('cantidad_stock', 0))
    categoria_id    = form_data.get('categoria_id', '').strip()

    # Paso 3: procesar imagen
    imagen_url = None
    if file and allowed_file(file.filename, allowed_extensions):
        filename    = secure_filename(file.filename)
        full_path   = os.path.join(upload_folder, filename)
        base, ext   = os.path.splitext(filename)
        counter     = 1
        # Evitar nombres duplicados
        while os.path.exists(full_path):
            filename  = f"{base}_{counter}{ext}"
            full_path = os.path.join(upload_folder, filename)
            counter  += 1
        file.save(full_path)
        imagen_url = f'/static/images/{filename}'

    # Paso 4: guardado en Firestore con ID personalizado
    nuevo_producto = {
        "descripcion":     descripcion,
        "valor_unitario":  valor_unitario,
        "unidad_medida":   unidad_medida,
        "cantidad_stock":  cantidad_stock,
        "categoria_id":    categoria_id,
        "imagen":          imagen_url,
    }
    db.collection('productos').document(str(nuevo_id)).set(nuevo_producto)
    return "Producto registrado exitosamente"

# === FUNCIÓN: Detalle de un producto ===
def fun_producto_detalle(id):
    """
    Recupera un producto por ID, construye su URL de imagen
    y renderiza 'producto_detalle.html'.
    """
    producto_ref = db.collection('productos').document(id)
    doc = producto_ref.get()
    if not doc.exists:
        return redirect(url_for('productos.productos'))

    producto = doc.to_dict()
    producto['id'] = id
    # URL de imagen: usa el campo 'imagen' o imagen por defecto
    if producto.get('imagen'):
        producto['imagen_url'] = producto['imagen']
    else:
        producto['imagen_url'] = url_for('static', filename='images/default.png')

    return render_template('producto_detalle.html', producto=producto)

# === FUNCIÓN: Editar un producto existente ===
def fun_editar_producto(id, form_data, file, upload_folder, allowed_extensions):
    """
    Actualiza los datos de un producto y su imagen (si se sube una nueva).
    """
    ref = db.collection('productos').document(id)
    doc = ref.get()
    if not doc.exists:
        flash("Producto no encontrado", "error")
        return redirect(url_for('productos.productos'))

    # Campos actualizados
    descripcion    = form_data.get('descripcion', '').strip()
    valor_unitario = float(form_data.get('valor_unitario', 0))
    unidad_medida  = form_data.get('unidad_medida', '').strip()
    cantidad_stock = int(form_data.get('cantidad_stock', 0))
    categoria_id   = form_data.get('categoria_id', '').strip()

    # Procesar nueva imagen si se sube
    imagen_url = doc.to_dict().get('imagen')
    if file and allowed_file(file.filename, allowed_extensions):
        filename    = secure_filename(file.filename)
        full_path   = os.path.join(upload_folder, filename)
        base, ext   = os.path.splitext(filename)
        counter     = 1
        while os.path.exists(full_path):
            filename  = f"{base}_{counter}{ext}"
            full_path = os.path.join(upload_folder, filename)
            counter  += 1
        file.save(full_path)
        imagen_url = f'/static/images/{filename}'

    # Actualizamos el documento
    ref.update({
        "descripcion":     descripcion,
        "valor_unitario":  valor_unitario,
        "unidad_medida":   unidad_medida,
        "cantidad_stock":  cantidad_stock,
        "categoria_id":    categoria_id,
        "imagen":          imagen_url,
    })
    flash("Producto actualizado exitosamente", "success")
    return redirect(url_for('productos.producto_detalle', id=id))
