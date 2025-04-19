# decorators.py

from flask import session, flash, redirect, url_for
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            flash("Debes iniciar sesión para acceder a esta página.", "error")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            rol = session.get('rol')
            if rol not in allowed_roles:
                flash("No tienes permiso para acceder a esta página.", "error")
                return redirect(url_for('inicio'))
            return f(*args, **kwargs)
        return decorated
    return decorator
