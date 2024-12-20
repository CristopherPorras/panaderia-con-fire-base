from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, session as flask_session
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import Base, Producto, Categoria, Cliente, Factura, DetalleFactura, Usuario
import os

# Configuración de Flask y SQLAlchemy
app = Flask(__name__)
app.secret_key = 'clave_secreta_para_flash_mensajes'

# Configuración de la base de datos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'mi_base_de_datos.db')}"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Crear las tablas si no existen
Base.metadata.create_all(engine)

# Configuración de subida de imágenes
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'images')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Sesión de base de datos
Session = scoped_session(sessionmaker(bind=engine))
db_session = Session()

# Rutas de Usuarios
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        usuario = db_session.query(Usuario).filter_by(email=email).first()
        if usuario and check_password_hash(usuario.password, password):
            flash(f"Bienvenido, {usuario.nombre}!", "success")
            flask_session['usuario_id'] = usuario.id
            return redirect(url_for('inicio'))
        else:
            flash("Usuario o contraseña incorrectos.", "error")
            return redirect(url_for('login'))

    return render_template('index.html')

@app.route('/logout')
def logout():
    flask_session.pop('usuario_id', None)
    flash("Sesión cerrada exitosamente.", "success")
    return redirect(url_for('login'))

@app.route('/index')
def index():
    return redirect(url_for('login'))

@app.route('/inicio')
def inicio():
    if 'usuario_id' not in flask_session:
        flash("Por favor, inicia sesión.", "error")
        return redirect(url_for('login'))
    return render_template('inicio.html')

# Ruta para productos
@app.route('/productos')
def productos():
    query = request.args.get('query', '')
    categoria_id = request.args.get('categoria')

    productos_query = db_session.query(Producto)

    if query:
        productos_query = productos_query.filter(Producto.descripcion.ilike(f"%{query}%"))
    if categoria_id:
        productos_query = productos_query.filter(Producto.categoria_id == int(categoria_id))

    productos = productos_query.all()
    categorias = db_session.query(Categoria).all()

    return render_template('productos.html', productos=productos, categorias=categorias)

# Ruta para detalle del producto
@app.route('/producto/<int:id>')
def producto_detalle(id):
    producto = db_session.query(Producto).get(id)
    if not producto:
        flash('El producto no existe.', 'error')
        return redirect(url_for('productos'))

    return render_template('producto_detalle.html', producto=producto)

# Ruta para facturar
@app.route('/facturar', methods=['GET', 'POST'])
def facturar():
    try:
        return render_template('facturar.html')
    except Exception as e:
        flash(f"Error al cargar la página de facturación: {e}", "error")
        return redirect(url_for('inicio'))

# Ruta para consultar facturas
@app.route('/consultar_facturas', methods=['GET'])
def consultar_facturas():
    try:
        return render_template('consultar_facturas.html')
    except Exception as e:
        flash(f"Error al cargar la página de consulta de facturas: {e}", "error")
        return redirect(url_for('inicio'))

# Ruta para registrar producto
@app.route('/registrar_producto', methods=['GET', 'POST'])
def registrar_producto():
    if request.method == 'POST':
        try:
            descripcion = request.form['descripcion']
            valor_unitario = request.form.get('valor_unitario', type=float)
            unidad_medida = request.form['unidad_medida']
            cantidad_stock = request.form.get('cantidad_stock', type=int)
            categoria_id = request.form.get('categoria_id', type=int)

            producto_existente = db_session.query(Producto).filter_by(descripcion=descripcion).first()
            if producto_existente:
                flash(f"El producto con descripción '{descripcion}' ya existe.", "error")
                return redirect(url_for('registrar_producto'))

            nuevo_producto = Producto(
                descripcion=descripcion,
                valor_unitario=valor_unitario,
                unidad_medida=unidad_medida,
                cantidad_stock=cantidad_stock,
                categoria_id=categoria_id,
                imagen=None  # Se inicializa sin imagen
            )

            if 'imagen' in request.files and request.files['imagen'].filename:
                file = request.files['imagen']
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                nuevo_producto.imagen = f"images/{filename}"

            db_session.add(nuevo_producto)
            db_session.commit()
            flash('Producto registrado con éxito', 'success')
            return redirect(url_for('productos'))
        except Exception as e:
            db_session.rollback()
            flash(f"Error al registrar el producto: {e}", "error")

    categorias = db_session.query(Categoria).all()
    return render_template('registrar_producto.html', categorias=categorias)

# Ruta para editar producto
@app.route('/editar_producto/<int:id>', methods=['GET', 'POST'])
def editar_producto(id):
    producto = db_session.query(Producto).get(id)
    if not producto:
        flash('El producto no existe.', 'error')
        return redirect(url_for('productos'))

    if request.method == 'POST':
        try:
            descripcion = request.form.get('descripcion', '').strip()
            valor_unitario = request.form.get('valor_unitario', type=float)
            unidad_medida = request.form.get('unidad_medida', '').strip()
            cantidad_stock = request.form.get('cantidad_stock', type=int)
            categoria_id = request.form.get('categoria_id', type=int)

            if 'imagen' in request.files and request.files['imagen'].filename:
                file = request.files['imagen']
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                producto.imagen = f"images/{filename}"

            producto.descripcion = descripcion
            producto.valor_unitario = valor_unitario
            producto.unidad_medida = unidad_medida
            producto.cantidad_stock = cantidad_stock
            producto.categoria_id = categoria_id

            db_session.commit()
            flash('Producto actualizado con éxito.', "success")
            return redirect(url_for('producto_detalle', id=producto.id))
        except Exception as e:
            db_session.rollback()
            flash(f"Error al actualizar el producto: {e}", "error")

    categorias = db_session.query(Categoria).all()
    return render_template('editar_producto.html', producto=producto, categorias=categorias)

# Ruta para favicon
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.static_folder),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    app.run(debug=True)

@app.context_processor
def inject_favicon():
    return {"favicon_url": url_for('static', filename='favicon.ico')}
