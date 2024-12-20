from sqlalchemy.ext.declarative import declarative_base

# Define Base para todos los modelos
Base = declarative_base()

# Importa los modelos
from .productos import Producto
from .clientes import Cliente
from .facturas import Factura, DetalleFactura
from .usuarios import Usuario
from .categoria import Categoria
