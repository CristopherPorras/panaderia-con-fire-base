#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from flask import Flask, session, flash

# Importamos el módulo, no sus nombres directamente
import extensions

# Inicializamos antes de cualquier cosa
extensions.init_extensions('delicias.json')

# Creamos la app de Flask
app = Flask(
    __name__,
    template_folder=os.path.join(os.getcwd(), 'templates')
)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'mi_clave_secreta')
app.config['UPLOAD_FOLDER']      = os.path.join(app.root_path, 'static', 'images')
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Context processor: inyecta datos del vendedor
@app.context_processor
def inject_user():
    # Usamos extensions.db que ya fue creado por init_extensions
    db = extensions.db
    if 'user_id' in session:
        doc = db.collection('vendedores').document(session['user_id']).get()
        if doc.exists:
            return dict(vendedor=doc.to_dict())
    return dict(vendedor={'nombre': 'Invitado'})

# Registramos los Blueprints tras haber inicializado db
from controllers.auth_controller        import auth_bp
from controllers.facturacion_controller import facturacion_bp
from controllers.productos_controller   import productos_bp
from controllers.clientes_controller    import clientes_bp
from controllers.vendedores_controller  import vendedores_bp

app.register_blueprint(auth_bp)
app.register_blueprint(facturacion_bp)
app.register_blueprint(productos_bp)
app.register_blueprint(clientes_bp)
app.register_blueprint(vendedores_bp)

# Arrancamos el servidor
if __name__ == '__main__':
    app.run(debug=True)
