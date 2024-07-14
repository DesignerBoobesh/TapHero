from flask import session, request
from modules.auth.schema import *
from flask import render_template, redirect
from models.user.queries import UserQueryOps
from modules.commons import mongo_transaction_with_retry
from pymongo.errors import PyMongoError
from custom_errors import *
from . import auth_bp
from models.user.base import User
from modules.auth.helpers import *
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import random
import string


@auth_bp.route('/auth/register', methods=['POST'])
def register():
    from app import mongo_db, mongo_session, session
    print(f"Registering user1")

    result_status = True
    result_msg = 'Authenticated successfully!'
    try:
        auth_register_params = AuthRegisterParams(
            email=request.form.get('email'),
            username=request.form.get('username'),
            password=request.form.get('password'),
        )
        # Perform additional validation if necessary
        print(f"Registering user2")
        existing_user = mongo_db['user'].find_one({"$or": [{"email": auth_register_params.email}, {"username": auth_register_params.username}]})
        if existing_user:
            print(f"Registering user333")

            result_status = False
            if existing_user.get("email") == auth_register_params.email:
                result_msg = "Email already registered."
                print(result_msg)
            elif existing_user.get("username") == auth_register_params.username:
                result_msg = "Username already taken."
                print(result_msg)

        session['email'] = request.form.get('email')
        session['username'] = request.form.get('username')
        session['password'] = request.form.get('password')
        print(f"Registering user3")
    except EmptyEmailError:
        result_status = False
        result_msg = 'Email can not be empty!'
    except InvalidEmail:
        result_status = False
        result_msg = 'Email is invalid!'
    except InvalidUsername:
        result_status = False
        result_msg = 'Username must be longer than 3 characters'
    except InvalidPassword:
        result_status = False
        result_msg = 'Password must be longer than 6 character long and contains at least 1 digit & 1 letter!'
    except Exception as e:
        result_status = False
        result_msg = str(e)
        print(f"Unexpected error: {result_msg}")
    
    if result_status == True:
                print(f"Registering user4")
                auth_register_params = AuthRegisterParams(
                    email=session.get('email'),
                    username=session.get('username'),
                    password=session.get('password'),
                )
                new_user = User(
                    email=auth_register_params.email,
                    username=auth_register_params.username,
                    password=auth_register_params.password,
                    favorite_list=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
                )
                
                user_query_ops = UserQueryOps(mongo_db, mongo_session)
                mongo_transaction_with_retry(mongo_session,lambda: user_query_ops.create(new_user))
                print(f"Registering user5")
                session['username'] = new_user.username
                return redirect('/my_profile')
    else:
        session['result_msg'] = result_msg
        return redirect('/auth')



@auth_bp.route('/auth/login', methods=['POST'])
def login():
    from app import (app, mongo_session, mongo_db)

    result_status = True
    result_msg = 'Authenticated successfully!'
    try:
        auth_login_params = AuthLoginParams(
            username= request.form.get('username'),
            password = request.form.get('password')
            )
        user = validate_and_get_user(auth_login_params, mongo_db, mongo_session)
        session['username'] = user.username
    
    except InvalidUsername:
        result_status = False
        result_msg = 'Username must be longer than 3 characters'
    except UserNotFound:
        result_status=False
        result_msg= 'This username is not registered'
    except InvalidPassword:
        result_status=False
        result_msg = 'Incorrect Password'
    except Exception as e:
        result_status = False
        result_msg = str(e)

    if result_status == True:
        return redirect('/my_profile')
    if result_status == False:
        session['result_msg'] = result_msg
        return redirect('/auth')

@auth_bp.route('/logout')
def logout():
    # Clear the session (log out the user)
    session.clear()
    # Redirect the user to index_unauthenticated.html
    return redirect('/')


@auth_bp.route('/auth', methods=['GET'])
def auth_view():
    
    result_msg = session.pop("result_msg", "")
    return render_template('auth.html', result_msg = result_msg)
