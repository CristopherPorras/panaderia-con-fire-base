from flask import render_template, request, redirect, url_for, flash
from firebase_admin import firestore

# Obtenemos el cliente de Firestore
db = firestore.client()

# ✅ Función para obtener clientes desde Firestore
def obtener_clientes():
    clientes_ref = db.collection('clientes')
    clientes_docs = clientes_ref.stream()

    # Convertimos los documentos en una lista de diccionarios
    clientes = [{"id": doc.id, **doc.to_dict()} for doc in clientes_docs]
    return clientes

# ✅ Función para registrar un nuevo cliente desde formulario
def registrar_cliente():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        documento = request.form.get('documento', '').strip()
        email = request.form.get('email', '').strip()
        telefono = request.form.get('telefono', '').strip()
        direccion = request.form.get('direccion', '').strip()

        # Validación de campos vacíos
        if not all([nombre, documento, email, telefono, direccion]):
            flash("Todos los campos son obligatorios.", "error")
            return redirect(url_for('registrar_cliente'))

        # Verificar si ya existe un cliente con ese documento
        clientes_ref = db.collection('clientes')
        cliente_existente = clientes_ref.where("documento", "==", documento).stream()

        if any(cliente_existente):
            flash("El documento ya está registrado.", "error")
            return redirect(url_for('registrar_cliente'))

        # Guardar cliente nuevo
        clientes_ref.add({
            "nombre": nombre,
            "documento": documento,
            "email": email,
            "telefono": telefono,
            "direccion": direccion
        })

        flash("Cliente registrado exitosamente.", "success")
        return redirect(url_for('inicio'))

    # Si no es POST, mostramos el formulario
    return render_template('registrar_cliente.html')
