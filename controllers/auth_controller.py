from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from extensions import db
from decorators import login_required
from werkzeug.security import check_password_hash
from extensions import db, PDFSHIFT_API_KEY      # si necesitas la API de PDFShift



auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario'].strip()
        password = request.form['password'].strip()
        ref = db.collection('vendedores').where('usuario', '==', usuario).stream()
        vendedor = next(ref, None)
        if vendedor and check_password_hash(vendedor.to_dict().get('contrasena', ''), password):
            session['user'] = usuario
            session['user_id'] = vendedor.id
            flash("Inicio de sesión exitoso.", "success")
            return redirect(url_for('auth.inicio'))
        flash("Usuario o contraseña incorrectos.", "error")
        return redirect(url_for('auth.login'))
    return render_template('index.html')

@auth_bp.route('/logout')
def logout():
    session.pop('user', None)
    flash("Sesión cerrada exitosamente.", "success")
    return redirect(url_for('auth.login'))

@auth_bp.route('/inicio')
@login_required
def inicio():
    return render_template('inicio.html')
