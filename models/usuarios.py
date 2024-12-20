
from sqlalchemy import Column, Integer, String
from models import Base  # Importa Base desde models/__init__.py

class Usuario(Base):
    __tablename__ = 'usuarios'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(150), nullable=False)
    email = Column(String(150), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    rol = Column(String(50), nullable=False, default="user")
