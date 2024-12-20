from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from werkzeug.security import generate_password_hash
from models import Base, Usuario, Producto, Categoria, Cliente, Factura, DetalleFactura

# Configuración de la base de datos
DATABASE_URL = "sqlite:///mi_base_de_datos.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Crear las tablas
Base.metadata.create_all(engine)

# Crear sesión de base de datos
Session = sessionmaker(bind=engine)
session = Session()

# Función para inicializar datos
def inicializar_datos():
    # Crear usuario inicial
    if not session.query(Usuario).filter_by(email="admin@delicias.com").first():
        usuario = Usuario(
            nombre="Admin",
            email="admin@delicias.com",
            password=generate_password_hash("admin123"),  # Contraseña cifrada
            rol="admin"
        )
        session.add(usuario)
        print("Usuario 'Admin' creado.")

    # Crear categorías iniciales
    if not session.query(Categoria).first():
        categorias = [
            Categoria(nombre="Panadería"),
            Categoria(nombre="Repostería"),
            Categoria(nombre="Bebidas"),
        ]
        session.add_all(categorias)
        print("Categorías iniciales creadas.")

    # Crear productos iniciales
    if not session.query(Producto).first():
        productos = [
            Producto(descripcion="Pan Francés", valor_unitario=1.5, unidad_medida="kg", cantidad_stock=100, categoria_id=1),
            Producto(descripcion="Torta de Chocolate", valor_unitario=15.0, unidad_medida="ud", cantidad_stock=20, categoria_id=2),
            Producto(descripcion="Café Americano", valor_unitario=2.0, unidad_medida="ud", cantidad_stock=50, categoria_id=3),
        ]
        session.add_all(productos)
        print("Productos iniciales creados.")

    # Guardar todos los cambios
    session.commit()
    print("Datos inicializados correctamente.")

# Ejecutar la inicialización
if __name__ == "__main__":
    inicializar_datos()
    session.close()
