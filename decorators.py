from flask import session, flash, redirect, url_for
from functools import wraps

def login_required(f):
    """
    Verifica que haya un usuario en sesión.
    Si no, redirige al login con mensaje de error.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            flash("Debes iniciar sesión para acceder a esta página.", "error")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated
