from sqlalchemy import create_engine, MetaData, Table, text
from sqlalchemy.exc import OperationalError

# Conexión a la base de datos
engine = create_engine('sqlite:///mi_base_de_datos.db')
meta = MetaData()

# Cargar las tablas existentes
meta.reflect(bind=engine)

try:
    # Acceder a la tabla productos
    productos = Table('productos', meta, autoload_with=engine)

    # Verificar si la columna ya existe
    if 'imagen' not in productos.c.keys():
        # Agregar la columna imagen
        with engine.connect() as conn:
            conn.execute(text('ALTER TABLE productos ADD COLUMN imagen TEXT'))
        print("Columna 'imagen' añadida con éxito.")
    else:
        print("La columna 'imagen' ya existe.")
except OperationalError as e:
    print(f"Error al modificar la tabla: {e}")
