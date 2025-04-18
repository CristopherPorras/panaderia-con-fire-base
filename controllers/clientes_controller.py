from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from decorators import login_required
from models.clientes import registrar_cliente, obtener_clientes
from extensions import db, PDFSHIFT_API_KEY 

clientes_bp = Blueprint('clientes', __name__)

@clientes_bp.route('/registrar_cliente', methods=['GET','POST'])
@login_required
def registrar_cliente_route():
    return registrar_cliente()

@clientes_bp.route('/clientes')
@login_required
def clientes():
    data = obtener_clientes()
    return render_template('clientes.html', clientes=data)

@clientes_bp.route('/editar_cliente/<id>', methods=['GET','POST'])
@login_required
def editar_cliente(id):
    ref = db.collection('clientes').document(id)
    if request.method=='POST':
        actualizado = {
            'nombre':request.form['nombre'],
            'documento':request.form['documento'],
            'email':request.form['email'],
            'telefono':request.form['telefono'],
            'direccion':request.form['direccion']
        }
        ref.update(actualizado)
        flash("Cliente actualizado con éxito","success")
        return redirect(url_for('clientes.clientes'))
    doc = ref.get()
    if doc.exists:
        cli = doc.to_dict(); cli['id']=doc.id
        return render_template('editar_cliente.html', cliente=cli)
    flash("Cliente no encontrado","error")
    return redirect(url_for('clientes.clientes'))

@clientes_bp.route('/eliminar_cliente/<id>', methods=['POST'])
@login_required
def eliminar_cliente(id):
    try:
        db.collection('clientes').document(id).delete()
        flash("Cliente eliminado exitosamente","success")
    except Exception as e:
        flash(f"Error: {e}","error")
    return redirect(url_for('clientes.clientes'))
