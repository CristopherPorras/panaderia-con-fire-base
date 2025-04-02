import firebase_admin
from flask import url_for, flash, redirect
from firebase_admin import firestore, db, credentials
from flask import Flask,render_template, request
from werkzeug.utils import secure_filename
import os

# Configuración de Firebase
cred = credentials.Certificate(os.path.join('instance/delicias.json'))
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://base-de-datos-panaderia-f4398-default-rtdb.firebaseio.com/',
    'projectId': 'base-de-datos-panaderia-f4398',  
    'storageBucket': 'base-de-datos-panaderia-f4398.firebasestorage.app',  
})



# Función para verificar las extensiones permitidas
def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


# Obtener la instancia de Firestore
db = firestore.client()

def fun_productos():
    # Obtener los productos de Firestore
    productos_ref = db.collection('productos')
    
    # Filtrar por búsqueda
    query = request.args.get('query', '')
    if query:
        productos_ref = productos_ref.where('descripcion', '>=', query).where('descripcion', '<=', query + '\uf8ff')

    # Filtrar por categoría (si se ha seleccionado)
    categoria_id = request.args.get('categoria')
    if categoria_id:
        productos_ref = productos_ref.where('categoria_id', '==', categoria_id)
    
    productos = productos_ref.stream()
    
    # Convertir los productos a una lista de diccionarios
    lista_productos = []
    for producto in productos:
        producto_dict = producto.to_dict()
        producto_dict['id'] = producto.id  # Añadir el id del documento
        lista_productos.append(producto_dict)
    
    # Obtener las categorías disponibles (esto asume que tienes una colección de categorías)
    categorias_ref = db.collection('categorias')
    categorias = categorias_ref.stream()
    lista_categorias = []
    for categoria in categorias:
        categoria_dict = categoria.to_dict()
        categoria_dict['id'] = categoria.id
        lista_categorias.append(categoria_dict)

    return render_template('productos.html', productos=lista_productos, categorias=lista_categorias) 

def fun_regis_productos(form_data, file, upload_folder, allowed_extensions):
    # Paso 1: Verificar si la colección 'productos' está vacía
    productos_ref = db.collection('productos')
    productos_existentes = productos_ref.limit(1).stream()  # Limita la consulta a un documento

    if not list(productos_existentes):  # Si no hay documentos en 'productos'
        # Reiniciar el contador a 0
        config_ref = db.collection('config').document('counters')
        config_ref.set({'ultimo_id': 0})  # Reinicia el contador
        ultimo_id = 0
    else:
        # Obtener el último ID del documento de configuración
        config_ref = db.collection('config').document('counters')
        config_doc = config_ref.get()
        if config_doc.exists:
            ultimo_id = config_doc.to_dict().get('ultimo_id', 0)  # Obtiene el último ID
        else:
            ultimo_id = 0
            config_ref.set({'ultimo_id': 0})

    nuevo_id = ultimo_id + 1  # Incrementa el contador

    # Paso 2: Actualizar el contador en Firestore
    config_ref.set({'ultimo_id': nuevo_id}, merge=True)

    # Paso 3: Procesar los datos del formulario
    descripcion = form_data.get('descripcion')
    valor_unitario = float(form_data.get('valor_unitario', 0))
    unidad_medida = form_data.get('unidad_medida')
    cantidad_stock = int(form_data.get('cantidad_stock', 0))
    categoria_id = form_data.get('categoria_id')
    imagen_url = None

    if file and allowed_file(file.filename, allowed_extensions):
        filename = secure_filename(file.filename)
        imagen_path = os.path.join(upload_folder, filename)

        # Renombrar si el archivo ya existe
        counter = 1
        base, extension = os.path.splitext(filename)
        while os.path.exists(imagen_path):
            filename = f"{base}_{counter}{extension}"
            imagen_path = os.path.join(upload_folder, filename)
            counter += 1

        file.save(imagen_path)
        imagen_url = f'/static/images/{filename}'  # URL relativa para la imagen

    # Paso 4: Guardar el producto en Firestore con el ID personalizado
    nuevo_producto = {
        "descripcion": descripcion,
        "valor_unitario": valor_unitario,
        "unidad_medida": unidad_medida,
        "cantidad_stock": cantidad_stock,
        "categoria_id": categoria_id,
        "imagen": imagen_url,
    }

    productos_ref.document(str(nuevo_id)).set(nuevo_producto)  # Usa el ID personalizado
    return "Producto registrado exitosamente"

def fun_producto_detalle(id):
    try:
        # Obtener el documento por su ID desde Firestore
        producto_ref = db.collection('productos').document(id)
        producto_doc = producto_ref.get()

        if producto_doc.exists:
            producto = producto_doc.to_dict()
            producto['id'] = id  # Incluye el ID del producto en el diccionario

            # Validar y construir la URL de la imagen
            if producto.get('imagen'):
                producto['imagen_url'] = url_for('static', filename=producto['imagen'])
            else:
                producto['imagen_url'] = url_for('static', filename='images/default.png')

            return render_template('producto_detalle.html', producto=producto)
        else:
            # Si el producto no existe, redirige a la página de productos
            return redirect(url_for('productos'))
    except Exception as e:
        print(f"Error al obtener el producto: {e}")
        return redirect(url_for('productos'))


def fun_editar_producto(id, form_data, file, upload_folder, allowed_extensions):
    descripcion = form_data.get('descripcion')
    valor_unitario = float(form_data.get('valor_unitario', 0))
    unidad_medida = form_data.get('unidad_medida')
    cantidad_stock = int(form_data.get('cantidad_stock', 0))
    categoria_id = form_data.get('categoria_id')
    
    # Obtener la URL actual de la imagen del producto
    producto_ref = db.collection('productos').document(id)
    producto = producto_ref.get()
    imagen_url = producto.to_dict().get('imagen') if producto.exists else None

    # Si se ha cargado una nueva imagen, procesarla
    if file and allowed_file(file.filename, allowed_extensions):
        filename = secure_filename(file.filename)
        imagen_path = os.path.join(upload_folder, filename)

        # Renombrar si el archivo ya existe
        counter = 1
        base, extension = os.path.splitext(filename)
        while os.path.exists(imagen_path):
            filename = f"{base}_{counter}{extension}"
            imagen_path = os.path.join(upload_folder, filename)
            counter += 1

        file.save(imagen_path)
        imagen_url = f'/static/images/{filename}'  # URL relativa para la imagen

    # Actualizar el producto en Firestore solo si el documento existe
    if producto.exists:
        producto_ref.update({
            "descripcion": descripcion,
            "valor_unitario": valor_unitario,
            "unidad_medida": unidad_medida,
            "cantidad_stock": cantidad_stock,
            "categoria_id": categoria_id,
            "imagen": imagen_url,
        })
        flash("Producto actualizado exitosamente", "success")
    else:
        flash("Producto no encontrado", "error")

    return redirect(url_for('producto_detalle', id=id))

