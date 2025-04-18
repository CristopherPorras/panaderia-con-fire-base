from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from extensions import db
from decorators import login_required
from models.productos import fun_productos, fun_regis_productos, fun_producto_detalle, fun_editar_producto
from models import facturacion
from extensions import db, PDFSHIFT_API_KEY 

productos_bp = Blueprint('productos', __name__)

@productos_bp.route('/productos')
@login_required
def productos():
    return fun_productos()

@productos_bp.route('/registrar_producto', methods=['GET','POST'])
@login_required
def registrar_producto():
    if request.method=='POST':
        msg = fun_regis_productos(
            request.form,
            request.files.get('imagen'),
            current_app.config['UPLOAD_FOLDER'],
            current_app.config['ALLOWED_EXTENSIONS']
        )
        flash(msg,"success")
        return redirect(url_for('productos.productos'))
    return render_template('registrar_producto.html')

@productos_bp.route('/producto/<id>')
@login_required
def producto_detalle(id):
    return fun_producto_detalle(id)

@productos_bp.route('/editar_producto/<id>', methods=['GET','POST'])
@login_required
def editar_producto(id):
    if request.method=='POST':
        return fun_editar_producto(
            id,
            request.form,
            request.files.get('imagen'),
            current_app.config['UPLOAD_FOLDER'],
            current_app.config['ALLOWED_EXTENSIONS']
        )
    doc = db.collection('productos').document(id).get()
    if doc.exists:
        prod = doc.to_dict(); prod['id']=id
        return render_template('editar_producto.html', producto=prod)
    flash("Producto no encontrado","error")
    return redirect(url_for('productos.productos'))

@productos_bp.route('/eliminar_producto/<id>', methods=['POST'])
@login_required
def eliminar_producto(id):
    try:
        db.collection('productos').document(id).delete()
        flash("Producto eliminado exitosamente","success")
    except Exception as e:
        flash(f"Error: {e}","error")
    return redirect(url_for('productos.productos'))

@productos_bp.route('/buscar_productos')
def buscar_productos():
    q = request.args.get('query','')
    return jsonify(facturacion.buscar_productos(q))
