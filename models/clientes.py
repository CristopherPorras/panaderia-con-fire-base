from sqlalchemy import column, Integer, String, Float, ForeignKey
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Cliente(Base):
    __tablename__ = 'clientes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(150), nullable=False)  # Nombre completo del cliente
    documento = Column(String(20), nullable=False, unique=True)  # Número de identificación único
    email = Column(String(150), nullable=True, unique=True)  # Correo electrónico opcional, debe ser único
    telefono = Column(String(15), nullable=True)  # Teléfono de contacto
    direccion = Column(String(250), nullable=True)  # Dirección del cliente

    def __repr__(self):
        return (
            f"<Cliente(id={self.id}, nombre={self.nombre}, documento={self.documento}, "
            f"email={self.email}, telefono={self.telefono}, direccion={self.direccion})>"
        )
