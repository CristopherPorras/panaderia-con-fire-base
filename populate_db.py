from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import Base, Categoria, Producto  # Asegúrate de que estos modelos existan

# Configurar la base de datos
DATABASE_URL = "sqlite:///mi_base_de_datos.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

# Agregar categorías iniciales
categorias_iniciales = [
    Categoria(nombre="Panadería"),
    Categoria(nombre="Repostería"),
    Categoria(nombre="Bebidas"),
    Categoria(nombre="Snacks"),
]

for categoria in categorias_iniciales:
    if not session.query(Categoria).filter_by(nombre=categoria.nombre).first():
        session.add(categoria)

# Agregar productos iniciales
productos_iniciales = [
    Producto(descripcion="Pan de Molde", valor_unitario=1.50, unidad_medida="kg", cantidad_stock=50, categoria_id=1),
    Producto(descripcion="Torta de Chocolate", valor_unitario=20.00, unidad_medida="unidad", cantidad_stock=10, categoria_id=2),
    Producto(descripcion="Jugo de Naranja", valor_unitario=2.50, unidad_medida="lt", cantidad_stock=30, categoria_id=3),
    Producto(descripcion="Chips de Papas", valor_unitario=1.00, unidad_medida="bolsa", cantidad_stock=100, categoria_id=4),
]

for producto in productos_iniciales:
    if not session.query(Producto).filter_by(descripcion=producto.descripcion).first():
        session.add(producto)

# Confirmar cambios en la base de datos
session.commit()
print("Base de datos poblada exitosamente.")

# Cerrar la sesión
session.close()
