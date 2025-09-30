from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user


def role_required(*roles):
    """Decorador para requerir uno o más roles específicos"""
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Debes iniciar sesión", "warning")
                return redirect(url_for("auth.login"))
            
            if current_user.rol not in roles:
                flash("No tenés permisos para acceder a esta sección", "danger")
                return redirect(url_for("dashboard"))
            
            return f(*args, **kwargs)
        return decorated_function
    return wrapper