# utils.py
from functools import wraps
from flask import session, redirect

def check_auth(func):
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        if 'username' not in session:
            session['result_msg'] = 'Auth Required'
            return redirect('/auth')
        else:
            return func(*args, **kwargs)

    return func_wrapper

def check_admin(func):
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        if session.get('username') != 'admin':
            session['result_msg'] = 'Not Permitted! Admin Role Required'
            return redirect('/auth')
        else:
            return func(*args, **kwargs)

    return func_wrapper
