from flask_sqlalchemy import SQLAlchemy

# Inicializamos SQLAlchemy
db = SQLAlchemy()

def init_app(app):
    # Vinculamos SQLAlchemy con la app Flask
    db.init_app(app)
    with app.app_context():
        db.create_all()  # Crea todas las tablas definidas en los modelos
