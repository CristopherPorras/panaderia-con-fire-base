from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from models import Base  # Importa Base desde models/__init__.py

class Producto(Base):
    __tablename__ = 'productos'

    id = Column(Integer, primary_key=True, autoincrement=True)
    descripcion = Column(String(300), unique=True, nullable=False)
    valor_unitario = Column(Float, nullable=False)
    unidad_medida = Column(String(3), nullable=False)
    cantidad_stock = Column(Float, nullable=False)
    categoria_id = Column(Integer, ForeignKey('categorias.id'), nullable=False)
    imagen = Column(String(300), nullable=True)

    # Relación con Categoria
    categoria = relationship("Categoria", back_populates="productos")

    def __repr__(self):
        return (
            f"<Producto(id={self.id}, descripcion={self.descripcion}, "
            f"valor_unitario={self.valor_unitario}, unidad_medida={self.unidad_medida}, "
            f"cantidad_stock={self.cantidad_stock}, categoria_id={self.categoria_id}, imagen={self.imagen})>"
        )
