from flask import render_template, request, redirect, url_for, flash
from firebase_admin import firestore
from werkzeug.security import generate_password_hash  # Cifrado seguro

db = firestore.client()

def registrar_vendedor():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        documento = request.form.get('documento', '').strip()
        usuario = request.form.get('usuario', '').strip()
        contrasena = request.form.get('contrasena', '').strip()
        telefono = request.form.get('telefono', '').strip()
        direccion = request.form.get('direccion', '').strip()

        if not all([nombre, documento, usuario, contrasena, telefono, direccion]):
            flash("Todos los campos son obligatorios.", "error")
            return redirect(url_for('registrar_vendedor_route'))

        vendedores_ref = db.collection('vendedores')
        usuario_existente = vendedores_ref.where("usuario", "==", usuario).stream()

        if any(usuario_existente):
            flash("Ese nombre de usuario ya está registrado.", "error")
            return redirect(url_for('registrar_vendedor_route'))

        # 🔐 Guardar contraseña cifrada
        vendedores_ref.add({
            "nombre": nombre,
            "documento": documento,
            "usuario": usuario,
            "contrasena": generate_password_hash(contrasena),
            "telefono": telefono,
            "direccion": direccion
        })

        flash("Vendedor registrado exitosamente.", "success")
        return redirect(url_for('inicio'))

    return render_template('registrar_vendedor.html')
