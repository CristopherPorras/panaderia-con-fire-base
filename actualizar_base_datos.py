from sqlalchemy import create_engine, MetaData, Table

# Configura la conexión a tu base de datos
engine = create_engine('sqlite:///mi_base_de_datos.db')
meta = MetaData()

# Refleja las tablas existentes en la base de datos
meta.reflect(bind=engine)

# Carga la tabla productos
productos = Table('productos', meta, autoload_with=engine)

# Añade la columna imagen si no existe
with engine.connect() as conn:
    if not 'imagen' in [c.name for c in productos.columns]:
        conn.execute('ALTER TABLE productos ADD COLUMN imagen TEXT')
        print("Columna 'imagen' añadida correctamente.")
    else:
        print("La columna 'imagen' ya existe en la tabla 'productos'.")
