# app/decorators.py

from functools import wraps
from flask import abort
from flask_login import current_user


def moderator_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'moderator':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
