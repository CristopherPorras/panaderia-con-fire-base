from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from models import Base  # Usa Base desde models/__init__.py

class Categoria(Base):
    __tablename__ = 'categorias'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), unique=True, nullable=False)

    # Relación con Producto
    productos = relationship("Producto", back_populates="categoria")

    def __repr__(self):
        return f"<Categoria(id={self.id}, nombre={self.nombre})>"
