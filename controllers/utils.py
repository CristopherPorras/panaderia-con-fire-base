
from functools import wraps
from flask import session, redirect, url_for, flash

def rol_requerido(*roles):
    def decorador(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            rol = session.get('user_rol')
            if rol not in roles:
                flash('No tienes permisos para acceder a esta sección.', 'error')

                #  Redirección segura según rol del usuario
                if rol == 'admin':
                    return redirect(url_for('auth.inicio_admin'))
                elif rol == 'vendedor':
                    return redirect(url_for('auth.inicio_vendedor'))
                else:
                    return redirect(url_for('auth.login'))  # fallback si no tiene rol
            return func(*args, **kwargs)
        return wrapper
    return decorador
