import os
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, session
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
    productos_ref = db.collection('productos')

    query_text = request.args.get('query', '').strip()
    if query_text:
        productos_ref = (
            productos_ref
            .where('descripcion', '>=', query_text)
            .where('descripcion', '<=', query_text + '')
        )

    categoria_id = request.args.get('categoria')
    if categoria_id:
        productos_ref = productos_ref.where('categoria_id', '==', categoria_id)

    productos_docs = productos_ref.stream()
    lista_productos = []
    for doc in productos_docs:
        data = doc.to_dict()
        data['id'] = doc.id
        lista_productos.append(data)

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
    config_ref = db.collection('config').document('counters')
    config_doc = config_ref.get()
    ultimo_id = config_doc.to_dict().get('ultimo_id', 0) if config_doc.exists else 0
    nuevo_id = ultimo_id + 1
    config_ref.set({'ultimo_id': nuevo_id}, merge=True)

    descripcion     = form_data.get('descripcion', '').strip()
    valor_unitario  = float(form_data.get('valor_unitario', 0))
    unidad_medida   = form_data.get('unidad_medida', '').strip()
    cantidad_stock  = int(form_data.get('cantidad_stock', 0))
    categoria_id    = form_data.get('categoria_id', '').strip()

    imagen_url = None
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
    producto_ref = db.collection('productos').document(id)
    doc = producto_ref.get()
    if not doc.exists:
        return redirect(url_for('productos.productos'))

    producto = doc.to_dict()
    producto['id'] = id
    if producto.get('imagen'):
        producto['imagen_url'] = producto['imagen']
    else:
        producto['imagen_url'] = url_for('static', filename='images/default.png')

    #  Muestra template según el rol
    if session.get('user_rol') == 'admin':
        return render_template('producto_detalle.html', producto=producto)
    else:
        return render_template('producto_detalle_vendedor.html', producto=producto)

# === FUNCIÓN: Editar un producto existente ===
def fun_editar_producto(id, form_data, file, upload_folder, allowed_extensions):
    ref = db.collection('productos').document(id)
    doc = ref.get()
    if not doc.exists:
        flash("Producto no encontrado", "error")
        return redirect(url_for('productos.productos'))

    descripcion    = form_data.get('descripcion', '').strip()
    valor_unitario = float(form_data.get('valor_unitario', 0))
    unidad_medida  = form_data.get('unidad_medida', '').strip()
    cantidad_stock = int(form_data.get('cantidad_stock', 0))
    categoria_id   = form_data.get('categoria_id', '').strip()

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
