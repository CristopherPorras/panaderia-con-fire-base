from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
from models import Base, Producto
import os

# Configuración de la base de datos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'mi_base_de_datos.db')}"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Crear las tablas si no existen
Base.metadata.create_all(engine)

# Sesión de base de datos
Session = scoped_session(sessionmaker(bind=engine))
db_session = Session()

# Borrar todos los productos de la tabla
def borrar_todos_los_productos():
    try:
        db_session.query(Producto).delete()
        db_session.commit()
        print("Todos los productos han sido eliminados correctamente.")
    except Exception as e:
        db_session.rollback()
        print(f"Error al borrar los productos: {e}")
    finally:
        db_session.close()

if __name__ == "__main__":
    borrar_todos_los_productos()
