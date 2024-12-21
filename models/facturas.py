from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from .clientes import Cliente  # Importar Cliente desde el paquete models

Base = declarative_base()

class Factura(Base):
    __tablename__ = 'facturas'

    id = Column(Integer, primary_key=True, autoincrement=True)
    numero = Column(String(20), unique=True, nullable=False)  # Número único de factura
    fecha = Column(Date, nullable=False)  # Fecha de emisión
    cliente_id = Column(Integer, ForeignKey('clientes.id'), nullable=False)  # Relación con Cliente
    total = Column(Float, nullable=False)  # Total de la factura

    # Relación con Cliente
    cliente = relationship("Cliente", back_populates="facturas")

    # Relación con los detalles de la factura
    detalles = relationship("DetalleFactura", back_populates="factura", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Factura(id={self.id}, numero={self.numero}, fecha={self.fecha}, cliente_id={self.cliente_id}, total={self.total})>"

class DetalleFactura(Base):
    __tablename__ = 'detalles_factura'

    id = Column(Integer, primary_key=True, autoincrement=True)
    factura_id = Column(Integer, ForeignKey('facturas.id'), nullable=False)  # Relación con Factura
    producto_id = Column(Integer, ForeignKey('productos.id'), nullable=False)  # Relación con Producto
    cantidad = Column(Float, nullable=False)  # Cantidad de producto
    precio_unitario = Column(Float, nullable=False)  # Precio por unidad
    total = Column(Float, nullable=False)  # Total por línea

    # Relación con Factura
    factura = relationship("Factura", back_populates="detalles")

    # Relación con Producto
    producto = relationship("Producto")

    def __repr__(self):
        return f"<DetalleFactura(id={self.id}, factura_id={self.factura_id}, producto_id={self.producto_id}, cantidad={self.cantidad}, total={self.total})>"
