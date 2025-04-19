from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from extensions import db
from decorators import login_required
import models.vendedores as vendedores_model
from extensions import db, PDFSHIFT_API_KEY 
from controllers.utils import rol_requerido

vendedores_bp = Blueprint('vendedores', __name__)

@vendedores_bp.route('/registrar-vendedor', methods=['GET','POST'])
@login_required
@rol_requerido('admin')  #  Solo admin puede registrar
def registrar_vendedor_route():
    return vendedores_model.registrar_vendedor()

@vendedores_bp.route('/vendedores')
@login_required
@rol_requerido('admin')  #  Solo admin puede ver la lista completa
def vendedores_lista():
    lista = vendedores_model.obtener_vendedores()
    return render_template('vendedores.html',
                           vendedores=[v for v in lista if v.get('usuario') != 'admin-root'])

@vendedores_bp.route('/editar_vendedor/<id>', methods=['GET','POST'])
@login_required
@rol_requerido('admin')  #  Solo admin puede editar
def editar_vendedor(id):
    ref = db.collection('vendedores').document(id)
    doc = ref.get()
    if not doc.exists:
        flash("Vendedor no encontrado", "error")
        return redirect(url_for('vendedores.vendedores_lista'))

    v = doc.to_dict()
    
    if v.get('usuario') == 'admin-root':
        flash("No se permite modificar este usuario especial.", "error")
        return redirect(url_for('vendedores.vendedores_lista'))

    if request.method == 'POST':
        updated = {
            'nombre': request.form['nombre'],
            'usuario': request.form['usuario'],
            'email': request.form['email'],
            'telefono': request.form['telefono'],
            'rol': request.form.get('rol', 'vendedor')  # ✅ CORREGIDO: guarda el rol
        }
        ref.update(updated)
        flash("Vendedor actualizado con éxito", "success")
        return redirect(url_for('vendedores.vendedores_lista'))

    v['id'] = doc.id
    return render_template('editar_vendedor.html', vendedor=v)

@vendedores_bp.route('/eliminar_vendedor/<id>', methods=['POST'])
@login_required
@rol_requerido('admin')  #  Solo admin puede eliminar
def eliminar_vendedor(id):
    doc = db.collection('vendedores').document(id).get()
    if not doc.exists:
        flash("Vendedor no encontrado.", "error")
        return redirect(url_for('vendedores.vendedores_lista'))

    v = doc.to_dict()

    if v.get('usuario') in ['admin-root', session.get('user')]:
        flash("No puedes eliminar este usuario especial.", "error")
        return redirect(url_for('vendedores.vendedores_lista'))

    db.collection('vendedores').document(id).delete()
    flash("Vendedor eliminado exitosamente", "success")
    return redirect(url_for('vendedores.vendedores_lista'))
