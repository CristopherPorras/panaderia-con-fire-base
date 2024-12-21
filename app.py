from flask import Flask, render_template, request, redirect, url_for, flash, session as flask_session, send_from_directory, jsonify
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import Base, Producto, Categoria, Cliente, Factura, DetalleFactura, Usuario
import os

# Configuraciones generales
# Establece las extensiones permitidas para los archivos a subir
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
# Define la carpeta donde se guardarán los archivos subidos
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static/uploads')

# Función para verificar extensiones permitidas
def allowed_file(filename):
    """Verifica si el archivo tiene una extensión permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Configuración de Flask y SQLAlchemy
app = Flask(__name__)
app.secret_key = 'clave_secreta_para_flash_mensajes'  # Llave secreta para sesiones y mensajes flash
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Crear el directorio para subir archivos si no existe
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Configuración de la base de datos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Directorio base del proyecto
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'mi_base_de_datos.db')}"  # URL de la base de datos
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})  # Motor de base de datos
Base.metadata.create_all(engine)  # Crea las tablas si no existen

# Configuración de sesión de base de datos
Session = scoped_session(sessionmaker(bind=engine))  # Configura una sesión segura
db_session = Session()

# Inicializar la base de datos con datos básicos
def inicializar_base_de_datos():
    """Crea un usuario administrador predeterminado si no existe"""
    if not db_session.query(Usuario).filter_by(email="admin@delicias.com").first():
        usuario = Usuario(
            nombre="Admin",
            email="admin@delicias.com",
            password=generate_password_hash("admin123"),
            rol="admin"
        )
        db_session.add(usuario)
        db_session.commit()
        print("Usuario administrador creado exitosamente.")

# Llama a la función para inicializar la base de datos
inicializar_base_de_datos()

# ---------------- Rutas de Autenticación ---------------- #
@app.route('/', methods=['GET', 'POST'])
def login():
    """Ruta para el inicio de sesión de usuarios"""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Verifica las credenciales del usuario
        usuario = db_session.query(Usuario).filter_by(email=email).first()
        if usuario and check_password_hash(usuario.password, password):
            flask_session['usuario_id'] = usuario.id
            flash(f"Bienvenido, {usuario.nombre}!", "success")
            return redirect(url_for('inicio'))
        flash("Usuario o contraseña incorrectos.", "error")
    return render_template('index.html')

@app.route('/logout')
def logout():
    """Cierra la sesión del usuario actual"""
    flask_session.pop('usuario_id', None)
    flash("Sesión cerrada exitosamente.", "success")
    return redirect(url_for('login'))

@app.route('/inicio')
def inicio():
    """Ruta para la página principal después de iniciar sesión"""
    if 'usuario_id' not in flask_session:
        flash("Por favor, inicia sesión.", "error")
        return redirect(url_for('login'))
    return render_template('inicio.html')

# ---------------- Rutas de Clientes ---------------- #
@app.route('/registrar_cliente', methods=['GET', 'POST'])
def registrar_cliente():
    """Permite registrar un nuevo cliente en la base de datos"""
    if request.method == 'POST':
        # Recupera datos del formulario
        nombre = request.form.get('nombre', '').strip()
        documento = request.form.get('documento', '').strip()
        email = request.form.get('email', '').strip()
        telefono = request.form.get('telefono', '').strip()
        direccion = request.form.get('direccion', '').strip()

        # Validaciones de campos obligatorios
        if not nombre or not documento or not email:
            flash("Por favor, complete todos los campos obligatorios (nombre, documento, email).", "error")
            return redirect(url_for('registrar_cliente'))

        # Verifica si el cliente ya está registrado
        cliente_existente = db_session.query(Cliente).filter((Cliente.email == email) | (Cliente.documento == documento)).first()
        if cliente_existente:
            flash("El cliente ya está registrado (correo o documento existente).", "error")
            return redirect(url_for('registrar_cliente'))

        # Crea un nuevo cliente
        nuevo_cliente = Cliente(
            nombre=nombre,
            documento=documento,
            email=email,
            telefono=telefono,
            direccion=direccion
        )
        db_session.add(nuevo_cliente)
        db_session.commit()
        flash("Cliente registrado con éxito.", "success")
        return redirect(url_for('inicio'))

    return render_template('registrar_cliente.html')

# ---------------- Rutas de Productos ---------------- #
@app.route('/productos')
def productos():
    """Muestra la lista de productos disponibles"""
    query = request.args.get('query', '')
    categoria_id = request.args.get('categoria')

    productos_query = db_session.query(Producto)
    # Filtrar productos por descripción y categoría
    if query:
        productos_query = productos_query.filter(Producto.descripcion.ilike(f"%{query}%"))
    if categoria_id:
        productos_query = productos_query.filter(Producto.categoria_id == int(categoria_id))

    productos = productos_query.all()
    categorias = db_session.query(Categoria).all()
    return render_template('productos.html', productos=productos, categorias=categorias)

@app.route('/producto/<int:id>')
def producto_detalle(id):
    """Muestra los detalles de un producto específico"""
    producto = db_session.get(Producto, id)
    if not producto:
        flash('El producto no existe.', 'error')
        return redirect(url_for('productos'))
    return render_template('producto_detalle.html', producto=producto)

@app.route('/registrar_producto', methods=['GET', 'POST'])
def registrar_producto():
    """Permite registrar un nuevo producto"""
    if request.method == 'POST':
        # Recupera datos del formulario
        descripcion = request.form.get('descripcion', '').strip()
        valor_unitario = request.form.get('valor_unitario', type=float)
        unidad_medida = request.form.get('unidad_medida', '').strip()
        cantidad_stock = request.form.get('cantidad_stock', type=int)
        categoria_id = request.form.get('categoria_id', type=int)

        # Validaciones de campos obligatorios
        if not descripcion or not valor_unitario or not unidad_medida or not cantidad_stock or not categoria_id:
            flash("Por favor, complete todos los campos obligatorios.", "error")
            return redirect(url_for('registrar_producto'))

        if valor_unitario <= 0 or cantidad_stock < 0:
            flash("El precio debe ser mayor a 0 y la cantidad no puede ser negativa.", "error")
            return redirect(url_for('registrar_producto'))

        # Manejo de la imagen del producto
        imagen = None
        if 'imagen' in request.files and request.files['imagen'].filename:
            file = request.files['imagen']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                imagen = f"uploads/{filename}"
            else:
                flash("Formato de archivo no permitido.", "error")
                return redirect(url_for('registrar_producto'))

        # Crea un nuevo producto
        nuevo_producto = Producto(
            descripcion=descripcion,
            valor_unitario=valor_unitario,
            unidad_medida=unidad_medida,
            cantidad_stock=cantidad_stock,
            categoria_id=categoria_id,
            imagen=imagen
        )
        db_session.add(nuevo_producto)
        db_session.commit()
        flash('Producto registrado con éxito.', "success")
        return redirect(url_for('productos'))

    categorias = db_session.query(Categoria).all()
    return render_template('registrar_producto.html', categorias=categorias)

@app.route('/editar_producto/<int:id>', methods=['GET', 'POST'])
def editar_producto(id):
    """Permite editar un producto existente"""
    producto = db_session.get(Producto, id)
    if not producto:
        flash("El producto no existe.", "error")
        return redirect(url_for('productos'))

    if request.method == 'POST':
        # Recupera datos del formulario
        producto.descripcion = request.form.get('descripcion', '').strip()
        producto.valor_unitario = request.form.get('valor_unitario', type=float)
        producto.unidad_medida = request.form.get('unidad_medida', '').strip()
        producto.cantidad_stock = request.form.get('cantidad_stock', type=int)
        producto.categoria_id = request.form.get('categoria_id', type=int)

        # Manejo de la imagen del producto
        if 'imagen' in request.files and request.files['imagen'].filename:
            file = request.files['imagen']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                producto.imagen = f"uploads/{filename}"
            else:
                flash("Formato de archivo no permitido.", "error")
                return redirect(url_for('editar_producto', id=id))

        db_session.commit()
        flash("Producto actualizado con éxito.", "success")
        return redirect(url_for('productos'))

    categorias = db_session.query(Categoria).all()
    return render_template('editar_producto.html', producto=producto, categorias=categorias)

@app.route('/eliminar_producto/<int:id>', methods=['POST'])
def eliminar_producto(id):
    """Permite eliminar un producto de la base de datos"""
    producto = db_session.get(Producto, id)
    if not producto:
        flash("El producto no existe.", "error")
        return redirect(url_for('productos'))

    db_session.delete(producto)
    db_session.commit()
    flash("Producto eliminado con éxito.", "success")
    return redirect(url_for('productos'))

# ---------------- Rutas de Facturación ---------------- #
@app.route('/facturar', methods=['GET', 'POST'])
def facturar():
    """Permite realizar el proceso de facturación"""
    if request.method == 'POST':
        cliente_id = request.form.get('cliente_id', type=int)
        productos = request.form.getlist('producto_id')
        cantidades = request.form.getlist('cantidad')

        if not cliente_id or not productos:
            flash("Debe seleccionar un cliente y al menos un producto.", "error")
            return redirect(url_for('facturar'))

        nueva_factura = Factura(cliente_id=cliente_id, total=0.0)
        db_session.add(nueva_factura)
        db_session.commit()

        total = 0.0
        for producto_id, cantidad in zip(productos, cantidades):
            producto = db_session.get(Producto, int(producto_id))
            if producto:
                subtotal = producto.valor_unitario * int(cantidad)
                total += subtotal
                detalle = DetalleFactura(
                    factura_id=nueva_factura.id,
                    producto_id=producto.id,
                    cantidad=int(cantidad),
                    precio_unitario=producto.valor_unitario,
                    total=subtotal
                )
                db_session.add(detalle)
        nueva_factura.total = total
        db_session.commit()

        flash("Factura creada con éxito.", "success")
        return redirect(url_for('productos'))

    clientes = db_session.query(Cliente).all()
    productos = db_session.query(Producto).all()
    return render_template('facturar.html', clientes=clientes, productos=productos)

@app.route('/consultar_facturas', methods=['GET'])
def consultar_facturas():
    """Muestra todas las facturas registradas"""
    facturas = db_session.query(Factura).all()
    return render_template('consultar_facturas.html', facturas=facturas)

# ---------------- Fin de rutas ---------------- #
@app.route('/favicon.ico')
def favicon():
    """Sirve el favicon para la aplicación"""
    return send_from_directory(os.path.join(app.static_folder),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

# ---------------- Iniciar aplicación ---------------- #
if __name__ == '__main__':
    app.run(debug=True)
