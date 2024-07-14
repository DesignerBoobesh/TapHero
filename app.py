#app.py
from flask import (Flask, session, request)
import pymongo
from os import environ
from functools import wraps
from flask import redirect
from flask import Flask
import pymongo
from os import environ
from modules.utils import check_auth, check_admin
from pymongo import MongoClient
import random
import string

app = Flask(__name__)
app.secret_key = 'my_secret_key'

MONGO_PASS = environ.get('MONGO_PASS')
app.config['MONGO_URI'] = 'mongodb+srv://mranewliz:1547mrmrmr@gemly.mbuqtyf.mongodb.net/?retryWrites=true&w=majority&appName=Gemly'

mongo_client = MongoClient(app.config['MONGO_URI'])
mongo_session = mongo_client.start_session()
mongo_db = mongo_client.mr

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

from modules.auth.auth import auth_bp
from modules.controller import controller_bp
app.register_blueprint(auth_bp)
app.register_blueprint(controller_bp)

if __name__ == "__main__":
    app.run(debug=False,host='0.0.0.0')
