from flask import flash, redirect, url_for, session
from functools import wraps
from database import get_user_by_username, get_user_by_id

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def login_user(username, password):
    user = get_user_by_username(username)
    if user and user.check_password(password):
        return user
    return None

def logout_user():
    session.pop('user_id', None)
    session.pop('username', None)