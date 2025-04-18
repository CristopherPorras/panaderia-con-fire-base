from flask import render_template, request, redirect, url_for, flash
from extensions import db  # Usamos el mismo cliente Firestore inicializado en extensions.py

#  Función para obtener todos los clientes desde Firestore
def obtener_clientes():
    clientes_ref = db.collection('clientes')
    clientes_docs = clientes_ref.stream()

    # Convertimos cada documento en un diccionario con su ID
    clientes = [
        {"id": doc.id, **doc.to_dict()}
        for doc in clientes_docs
    ]
    return clientes

#  Función para manejar el registro de un nuevo cliente desde un formulario
def registrar_cliente():
    if request.method == 'POST':
        # Recogemos y limpiamos los campos del formulario
        nombre     = request.form.get('nombre', '').strip()
        documento  = request.form.get('documento', '').strip()
        email      = request.form.get('email', '').strip()
        telefono   = request.form.get('telefono', '').strip()
        direccion  = request.form.get('direccion', '').strip()

        # Validación: todos los campos son obligatorios
        if not all([nombre, documento, email, telefono, direccion]):
            flash("Todos los campos son obligatorios.", "error")
            return redirect(url_for('clientes.registrar_cliente_route'))

        # Verificamos si ya existe un cliente con ese documento
        clientes_ref       = db.collection('clientes')
        consulta_existente = clientes_ref.where("documento", "==", documento).stream()
        if any(consulta_existente):
            flash("El documento ya está registrado.", "error")
            return redirect(url_for('clientes.registrar_cliente_route'))

        # Guardamos el nuevo cliente en Firestore
        clientes_ref.add({
            "nombre":    nombre,
            "documento": documento,
            "email":     email,
            "telefono":  telefono,
            "direccion": direccion
        })

        flash("Cliente registrado exitosamente.", "success")
        return redirect(url_for('clientes.clientes'))

    # Si no es POST, simplemente renderizamos el formulario
    return render_template('registrar_cliente.html')
