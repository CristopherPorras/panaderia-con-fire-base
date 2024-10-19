from flask import Flask, render_template

app = Flask(__name__)

# Ruta para la página de inicio
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para la página de facturar
@app.route('/facturar')
def facturar():
    return render_template('facturar.html')

# Ruta para la página de consultar facturas
@app.route('/consultar-facturas')
def consultar_facturas():
    return render_template('consultar-facturas.html')

# Ruta para la página de inicio
@app.route('/inicio')
def inicio():
    return render_template('inicio.html')

# Ruta para la página de pedidos
@app.route('/pedidos')
def pedidos():
    return render_template('pedidos.html')

# Ruta para la página de productos
@app.route('/productos')
def productos():
    return render_template('productos.html')

# NUEVA RUTA para el detalle del producto
@app.route('/producto/<nombre>')
def producto_detalle(nombre):
    return render_template('producto_detalle.html', nombre=nombre)

if __name__ == '__main__':
    app.run(debug=True)

