from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import Base, Usuario

# Configuración de base de datos
DATABASE_URL = "sqlite:///mi_base_de_datos.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

# Crear usuario inicial
nuevo_usuario = Usuario(
    nombre="Admin",
    email="admin@delicias.com",
    password="admin123",  # En producción, usa contraseñas cifradas
    rol="admin"
)

# Verificar si ya existe un usuario con este correo
if not session.query(Usuario).filter_by(email=nuevo_usuario.email).first():
    session.add(nuevo_usuario)
    session.commit()
    print("Usuario inicial creado exitosamente.")
else:
    print("El usuario ya existe.")

session.close()
