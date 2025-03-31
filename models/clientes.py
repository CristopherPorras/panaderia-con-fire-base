from flask import render_template, request, redirect, url_for, flash
from firebase_admin import firestore

db = firestore.client()

def obtener_clientes():
    """Obtiene la lista de clientes desde Firestore."""
    clientes_ref = db.collection('clientes')
    clientes_docs = clientes_ref.stream()

    clientes = [{"id": doc.id, **doc.to_dict()} for doc in clientes_docs]  # Extraer datos
    return clientes

def registrar_cliente():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        documento = request.form.get('documento', '').strip()
        email = request.form.get('email', '').strip()
        telefono = request.form.get('telefono', '').strip()
        direccion = request.form.get('direccion', '').strip()

        if not all([nombre, documento, email, telefono, direccion]):
            flash("Todos los campos son obligatorios.", "error")
            return redirect(url_for('registrar_cliente'))

        clientes_ref = db.collection('clientes')
        cliente_existente = clientes_ref.where("documento", "==", documento).stream()

        if any(cliente_existente):
            flash("El documento ya está registrado.", "error")
            return redirect(url_for('registrar_cliente'))

        clientes_ref.add({
            "nombre": nombre,
            "documento": documento,
            "email": email,
            "telefono": telefono,
            "direccion": direccion
        })

        flash("Cliente registrado exitosamente.", "success")
        return redirect(url_for('inicio'))

    return render_template('registrar_cliente.html')