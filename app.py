# ==== IMPORTACIONES ====
import os
import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from models import facturacion
from models.productos import db, fun_productos, fun_regis_productos, fun_producto_detalle, fun_editar_producto
from models.clientes import registrar_cliente, obtener_clientes
from models import vendedores
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash
from functools import wraps

# ==== INICIALIZACIÓN DE FLASK ====
app = Flask(__name__, template_folder=os.path.join(os.getcwd(), 'templates'))
app.secret_key = 'mi_clave_secreta'

# ==== CONFIGURACIÓN DE SUBIDAS ====
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'images')
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# ==== DECORADOR PARA PROTEGER RUTAS ====
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash("Debes iniciar sesión para acceder a esta página.", "error")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ==== RUTA DE INICIO ====
@app.route('/inicio')
@login_required
def inicio():
    return render_template('inicio.html')

# ==== LOGIN ====
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario'].strip()
        password = request.form['password'].strip()

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
    session.pop('user', None)
    flash("Sesión cerrada exitosamente.", "success")
    return redirect(url_for('login'))

# ==== FACTURACIÓN ====
@app.route('/facturar', methods=['GET', 'POST'])
@login_required
def facturacion_page():
    if request.method == 'POST':
        numero_factura = facturacion.guardar_factura(request.form)
        return redirect(url_for('facturacion_page'))

    numero_factura = facturacion.obtener_numero_factura()
    clientes_ref = db.collection("clientes").stream()
    clientes = [{"id": cliente.id, "nombre": cliente.to_dict().get("nombre")} for cliente in clientes_ref]

    return render_template('facturar.html', numero_factura=numero_factura, clientes=clientes)

@app.route("/facturar", methods=["POST"])
@login_required
def guardar_factura():
    facturacion.guardar_factura(request.form)
    return redirect(url_for("facturacion_page"))

# ==== CONSULTA DE FACTURAS ====
@app.route('/consultar_facturas')
@login_required
def consultar_facturas():
    query = request.args.get('query', '')
    fecha = request.args.get('fecha', '')
    facturas = facturacion.obtener_facturas_filtradas(query=query, fecha=fecha)

    # Prevención de error: aseguramos que cada detalle tenga 'producto' y 'total'
    for factura in facturas:
        for detalle in factura.get('detalles', []):
            if 'producto' not in detalle:
                detalle['producto'] = {'id': 'N/A', 'nombre': 'Producto desconocido'}
            if 'total' not in detalle:
                detalle['total'] = 0

    return render_template('consultar_facturas.html', facturas=facturas)


# ==== PRODUCTOS ====
@app.route('/productos', methods=['GET'])
@login_required
def productos():
    return fun_productos()

@app.route('/registrar_producto', methods=['GET', 'POST'])
@login_required
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
@login_required
def producto_detalle(id):
    return fun_producto_detalle(id)

@app.route('/editar_producto/<id>', methods=['GET', 'POST'])
@login_required
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
@login_required
def eliminar_producto(id):
    try:
        producto_ref = db.collection('productos').document(id)
        producto_ref.delete()
        flash("Producto eliminado exitosamente", "success")
    except Exception as e:
        flash(f"Error al eliminar el producto: {e}", "error")
    return redirect(url_for('productos'))

# ==== CLIENTES ====
@app.route('/registrar_cliente', methods=['GET', 'POST'])
@login_required
def registrar_cliente_route():
    return registrar_cliente()

@app.route('/clientes')
@login_required
def clientes():
    clientes_lista = obtener_clientes()
    return render_template('clientes.html', clientes=clientes_lista)

@app.route('/editar_cliente/<id>', methods=['GET', 'POST'])
@login_required
def editar_cliente(id):
    cliente_ref = db.collection('clientes').document(id)
    if request.method == 'POST':
        datos_actualizados = {
            'nombre': request.form['nombre'],
            'documento': request.form['documento'],
            'email': request.form['email'],
            'telefono': request.form['telefono'],
            'direccion': request.form['direccion']
        }
        cliente_ref.update(datos_actualizados)
        flash("Cliente actualizado con éxito", "success")
        return redirect(url_for('clientes'))

    cliente_doc = cliente_ref.get()
    if cliente_doc.exists:
        cliente = cliente_doc.to_dict()
        cliente['id'] = cliente_doc.id
        return render_template('editar_cliente.html', cliente=cliente)
    else:
        flash("Cliente no encontrado", "error")
        return redirect(url_for('clientes'))

@app.route('/eliminar_cliente/<id>', methods=['POST'])
@login_required
def eliminar_cliente(id):
    try:
        cliente_ref = db.collection('clientes').document(id)
        cliente_ref.delete()
        flash("Cliente eliminado exitosamente", "success")
    except Exception as e:
        flash(f"Error al eliminar el cliente: {e}", "error")
    return redirect(url_for('clientes'))

# ==== VENDEDORES ====
@app.route('/registrar-vendedor', methods=['GET', 'POST'])
@login_required
def registrar_vendedor_route():
    return vendedores.registrar_vendedor()

@app.route('/vendedores')
@login_required
def vendedores_lista():
    from models.vendedores import obtener_vendedores
    lista = obtener_vendedores()
    # ✅ Filtramos el usuario especial
    lista = [v for v in lista if v.get('usuario') != 'admin-root']
    return render_template('vendedores.html', vendedores=lista)


@app.route('/editar_vendedor/<id>', methods=['GET', 'POST'])
@login_required
def editar_vendedor(id):
    vendedor_ref = db.collection('vendedores').document(id)
    vendedor_doc = vendedor_ref.get()

    if vendedor_doc.exists:
        vendedor = vendedor_doc.to_dict()

        # 🚫 Si se intenta acceder al usuario protegido admin-root, redirige con mensaje
        if vendedor.get('usuario') == 'admin-root':
            flash("No se permite modificar este usuario especial.", "error")
            return redirect(url_for('vendedores_lista'))

        if request.method == 'POST':
            datos_actualizados = {
                'nombre': request.form['nombre'],
                'usuario': request.form['usuario'],
                'email': request.form['email'],
                'telefono': request.form['telefono']
            }
            vendedor_ref.update(datos_actualizados)
            flash("Vendedor actualizado con éxito", "success")
            return redirect(url_for('vendedores_lista'))

        vendedor['id'] = vendedor_doc.id
        return render_template('editar_vendedor.html', vendedor=vendedor)

    flash("Vendedor no encontrado", "error")
    return redirect(url_for('vendedores_lista'))


@app.route('/eliminar_vendedor/<id>', methods=['POST'])
@login_required
def eliminar_vendedor(id):
    vendedor_doc = db.collection('vendedores').document(id).get()

    if vendedor_doc.exists:
        vendedor = vendedor_doc.to_dict()

        # 🚫 Bloquear eliminación de admin-root o del usuario logueado
        if vendedor.get('usuario') == 'admin-root' or vendedor.get('usuario') == session.get('user'):
            flash("No puedes eliminar este usuario especial.", "error")
            return redirect(url_for('vendedores_lista'))

        db.collection('vendedores').document(id).delete()
        flash("Vendedor eliminado exitosamente", "success")
    else:
        flash("Vendedor no encontrado.", "error")

    return redirect(url_for('vendedores_lista'))


# ==== INICIAR SERVIDOR ====
if __name__ == '__main__':
    app.run(debug=True)
