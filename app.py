import firebase_admin
from firebase_admin import credentials, firestore, db
from flask import Flask, render_template, request, redirect, url_for, session, flash
from models.productos_python import db, fun_productos, fun_regis_productos, fun_producto_detalle, fun_editar_producto
from werkzeug.utils import secure_filename
import os

# Inicialización de la aplicación

app = Flask(__name__, template_folder=os.path.join(os.getcwd(), 'templates'))
app.secret_key = 'mi_clave_secreta'  # Cambia esto por una clave más segura

# Guardar imagenes
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'images')
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Rutas de la aplicación
@app.route('/inicio')
def inicio():
    """Ruta para la página principal después de iniciar sesión"""
    if 'user' not in session:
        flash("Por favor, inicia sesión.", "error")
        return redirect(url_for('login'))
    return render_template('inicio.html')

@app.route('/', methods=['GET', 'POST'])
def login():
    """Ruta para la página de inicio de sesión"""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Simulación de autenticación
        if email == "admin@delicias.com" and password == "1234":
            session['user'] = email  # Guarda al usuario en la sesión
            flash("Inicio de sesión exitoso.", "success")
            return redirect(url_for('inicio'))
        flash("Credenciales incorrectas.", "error")
        return redirect(url_for('login'))
    
    # Si es un GET, muestra el formulario de login
    return render_template('index.html')

@app.route('/logout')
def logout():
    """Cierra la sesión del usuario actual"""
    session.pop('user', None)  # Elimina al usuario de la sesión
    flash("Sesión cerrada exitosamente.", "success")
    return redirect(url_for('login'))

# Otras rutas
@app.route('/facturar')
def facturar():
    return render_template('facturar.html')

@app.route('/consultar_facturas')
def consultar_facturas():
    return render_template('consultar_facturas.html')

@app.route('/productos', methods=['GET'])
def productos():
    return fun_productos()


@app.route('/registrar_producto', methods=['GET', 'POST'])
def registrar_producto():
    if request.method == 'POST':
        mensaje = fun_regis_productos(
            request.form,
            request.files.get('imagen'),
            app.config['UPLOAD_FOLDER'],
            app.config['ALLOWED_EXTENSIONS']
        )
        flash(mensaje, "success")
        return redirect(url_for('productos'))
    return render_template('registrar_producto.html')


@app.route('/producto/<id>', methods=['GET'])
def producto_detalle(id):
    return fun_producto_detalle(id)


@app.route('/editar_producto/<id>', methods=['GET', 'POST'])
def editar_producto(id):
    print(f"ID del producto recibido: {id}")  # Depuración
    if request.method == 'POST':
        form_data = request.form
        file = request.files.get('imagen')
        upload_folder = app.config['UPLOAD_FOLDER']
        allowed_extensions = app.config['ALLOWED_EXTENSIONS']
        
        return fun_editar_producto(id, form_data, file, upload_folder, allowed_extensions)
    else:
        producto_ref = db.collection('productos').document(id)
        producto_doc = producto_ref.get()

        if producto_doc.exists:
            producto = producto_doc.to_dict()
            producto['id'] = id  # Añadir el id al diccionario del producto
            print(f"Producto obtenido: {producto}")  # Depuración
            return render_template('editar_producto.html', producto=producto)
        else:
            print("Producto no encontrado")  # Depuración
            flash("Producto no encontrado", "error")
            return redirect(url_for('productos'))

@app.route('/eliminar_producto/<id>', methods=['POST'])
def eliminar_producto(id):
    try:
        producto_ref = db.collection('productos').document(id)
        producto_ref.delete()
        flash("Producto eliminado exitosamente", "success")
    except Exception as e:
        flash(f"Error al eliminar el producto: {e}", "error")
    
    return redirect(url_for('productos'))

@app.route('/registrar_cliente')
def registrar_cliente():
    return render_template('registrar_cliente.html')

# Creación de categorías al iniciar la app
if __name__ == '__main__':
    app.run(debug=True)
