from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from extensions import db
from decorators import login_required
from werkzeug.security import check_password_hash
from extensions import db, PDFSHIFT_API_KEY  # si necesitas la API de PDFShift
from controllers.utils import rol_requerido  # ✅ necesario si vas a usar el decorador

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario'].strip()
        password = request.form['password'].strip()
        
        # Consultamos en la colección "vendedores"
        ref = db.collection('vendedores').where('usuario', '==', usuario).stream()
        vendedor = next(ref, None)
        
        if vendedor and check_password_hash(vendedor.to_dict().get('contrasena', ''), password):
            session['user'] = usuario
            session['user_id'] = vendedor.id
            rol = vendedor.to_dict().get('rol', 'vendedor')
            session['user_rol'] = rol
            flash("Inicio de sesión exitoso.", "success")

            # ✅ Redirecciona según el rol
            if rol == 'admin':
                return redirect(url_for('auth.inicio_admin'))
            else:
                return redirect(url_for('auth.inicio_vendedor'))

        flash("Usuario o contraseña incorrectos.", "error")
        return redirect(url_for('auth.login'))

    return render_template('index.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("Sesión cerrada exitosamente.", "success")
    return redirect(url_for('auth.login'))

@auth_bp.route('/inicio_admin')
@login_required
@rol_requerido('admin')
def inicio_admin():
    return render_template('inicio.html')  # este es el panel principal del admin

@auth_bp.route('/inicio_vendedor')
@login_required
@rol_requerido('vendedor', 'admin')  # opcional: admin también puede verlo
def inicio_vendedor():
    return render_template('inicio_vendedor.html')  # este es el nuevo panel para vendedores
