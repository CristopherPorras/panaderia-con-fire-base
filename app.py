import firebase_admin
from firebase_admin import credentials, firestore, db
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from models import facturacion
from models.facturacion import registrar_factura
from models.productos import db, fun_productos, fun_regis_productos, fun_producto_detalle, fun_editar_producto
from models.clientes import registrar_cliente, obtener_clientes
from models import vendedores  # <-- NUEVO IMPORT
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash  # <-- Para comparar contraseñas cifradas
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
        usuario = request.form['usuario'].strip()
        password = request.form['password'].strip()

        # Buscar el vendedor por su nombre de usuario en Firestore
        vendedores_ref = db.collection('vendedores')
        query = vendedores_ref.where('usuario', '==', usuario).stream()
        vendedor = next(query, None)

        if vendedor:
            datos = vendedor.to_dict()
            if check_password_hash(datos.get('contrasena', ''), password):
                session['user'] = datos['usuario']
                flash("Inicio de sesión exitoso.", "success")
                return redirect(url_for('inicio'))
            else:
                flash("Contraseña incorrecta.", "error")
        else:
            flash("Usuario no encontrado.", "error")

        return redirect(url_for('login'))

    return render_template('index.html')

@app.route('/logout')
def logout():
    """Cierra la sesión del usuario actual"""
    session.pop('user', None)
    flash("Sesión cerrada exitosamente.", "success")
    return redirect(url_for('login'))

@app.route('/facturar', methods=['GET', 'POST'])
def facturacion_page():
    if request.method == 'POST':
        numero_factura = facturacion.guardar_factura(request.form)
        return redirect(url_for('facturacion_page'))

    numero_factura = facturacion.obtener_numero_factura()
    clientes_ref = db.collection("clientes").stream()
    clientes = [{"id": cliente.id, "nombre": cliente.to_dict().get("nombre")} for cliente in clientes_ref]

    return render_template('facturar.html', numero_factura=numero_factura, clientes=clientes)

@app.route('/consultar_facturas')
def consultar_facturas():
    return render_template('consultar_facturas.html')

@app.route('/productos', methods=['GET'])
def productos():
    return fun_productos()

@app.route("/facturar", methods=["POST"])
def guardar_factura():
    facturacion.guardar_factura(request.form)
    return redirect(url_for("facturar.html"))

@app.route('/buscar_productos', methods=['GET'])
def buscar_productos():
    query = request.args.get('query', '')
    productos = facturacion.buscar_productos(query)
    return jsonify(productos)

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
            producto['id'] = id
            return render_template('editar_producto.html', producto=producto)
        else:
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

@app.route('/registrar_cliente', methods=['GET', 'POST'])
def registrar_cliente_route():
    return registrar_cliente()

# NUEVA RUTA REGISTRO DE VENDEDOR
@app.route('/registrar-vendedor', methods=['GET', 'POST'])
def registrar_vendedor_route():
    return vendedores.registrar_vendedor()

# Ejecutar la app
if __name__ == '__main__':
    app.run(debug=True)
