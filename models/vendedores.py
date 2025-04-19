from flask import render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash
from extensions import db  # Cliente Firestore inicializado en extensions.py

def registrar_vendedor():
    if request.method == 'POST':
        nombre     = request.form.get('nombre', '').strip()
        documento  = request.form.get('documento', '').strip()
        usuario    = request.form.get('usuario', '').strip()
        contrasena = request.form.get('contrasena', '').strip()
        telefono   = request.form.get('telefono', '').strip()
        direccion  = request.form.get('direccion', '').strip()
        # Nuevo campo rol con valor por defecto 'vendedor'
        rol        = request.form.get('rol', 'vendedor').strip()

        # Todos los campos son obligatorios (salvo rol, que tiene default)
        if not all([nombre, documento, usuario, contrasena, telefono, direccion]):
            flash("Todos los campos son obligatorios.", "error")
            return redirect(url_for('vendedores.registrar_vendedor_route'))

        vendedores_ref = db.collection('vendedores')
        # Comprobar si el usuario ya existe
        existe = vendedores_ref.where("usuario", "==", usuario).stream()
        if any(existe):
            flash("Ese nombre de usuario ya está registrado.", "error")
            return redirect(url_for('vendedores.registrar_vendedor_route'))

        # Guardar el nuevo vendedor con contraseña cifrada y rol
        vendedores_ref.add({
            "nombre":     nombre,
            "documento":  documento,
            "usuario":    usuario,
            "contrasena": generate_password_hash(contrasena),
            "telefono":   telefono,
            "direccion":  direccion,
            "rol":        rol
        })

        flash("Vendedor registrado exitosamente.", "success")
        # Redirigir a la lista de vendedores
        return redirect(url_for('vendedores.vendedores_lista'))

    # Si no es POST, renderizamos el formulario
    return render_template('registrar_vendedor.html')


def obtener_vendedores():
    vendedores_ref = db.collection('vendedores').stream()
    return [{"id": doc.id, **doc.to_dict()} for doc in vendedores_ref]
