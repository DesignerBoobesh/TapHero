#modules/controller.py
#from app import (app, mongo_session, mongo_db)
from flask import render_template, redirect, request , session
from modules.utils import check_auth, check_admin
from flask import render_template, redirect
from models.item.queries import ItemQueryOps
from models.user.queries import UserQueryOps
from models.review.queries import ReviewQueryOps
from models.item.base import Item
from models.review.base import Review
from models.user.base import User
from modules.commons import mongo_transaction_with_retry
from modules.schema import *
from pymongo.errors import PyMongoError
from custom_errors import *
from . import controller_bp
from flask import render_template, redirect, request
from modules.schema import CreateItemParams
from pymongo.errors import PyMongoError
from custom_errors import *
from pymongo import MongoClient
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import random
import string
from math import ceil
from flask import Flask, request, jsonify, session


#from flask import Blueprint

#controller_bp = Blueprint('controller', __name__)

@controller_bp.route('/', methods=['GET'])
def index():
    from app import mongo_db, mongo_session, request, session
    result_msg = session.pop("result_msg", "")
    
    # If user is logged in, render index.html
    item_query_ops = ItemQueryOps(mongo_db, mongo_session)
    category = request.args.get('category', None)
    if category is None or category == "All":
        items = mongo_transaction_with_retry(mongo_session,lambda: item_query_ops.search({ 'is_active': "true"}, limit=100))
    else:
        items = mongo_transaction_with_retry(mongo_session,lambda: item_query_ops.search({"category": category, 'is_active': "true"}, limit=100))

    items.reverse()

    page = request.args.get('page', default=1, type=int)
    items_per_page = 10
    total_items = len(items)
    total_pages = ceil(total_items / items_per_page)
    start_index = (page - 1) * items_per_page
    end_index = start_index + items_per_page
    items_for_page = items[start_index:end_index]

    return render_template('index.html', result_msg=result_msg, items=items_for_page, total_pages=total_pages, current_page=page)

    
@controller_bp.route('/portal', methods=['GET'])
def portal():
    if 'username' in session:
        return redirect('/my_profile')
    else:
        return redirect('/auth')

@controller_bp.route('/create_item', methods=['GET','POST'])
def create_item():
    from app import mongo_db, mongo_session, request, session
    from models.item.queries import ItemQueryOps
    from models.item.base import Item
    print("deneme1")
    if request.method == 'GET':
        result_msg = session.pop("result_msg", "")
        return render_template('create_item.html', result_msg=result_msg)
    if request.method == 'POST':
        print("deneme2")
        result_status = True
        result_msg = 'Item created successfully!'
        try:
            print("deneme3")
            price = request.form.get('price')

            form_data = {}
            form_data = {key: value for key, value in request.form.items() if value }
            #create_item_params = CreateItemParams(**form_data)
            # Create a new item with non-empty fields
            #print(create_item_params)
            #new_item = Item(**create_item_params.dict())
            #print(new_item)
            if form_data['image']:
                x=0
            else:
                form_data['image']="https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Bitcoin.svg/1200px-Bitcoin.svg.png"
            item_collection = mongo_db['item']
            item_collection.insert_one(form_data)
            #item_data = {k: v for k, v in create_item_params.dict().items() if v is not None and v != ''}
            #new_item = Item(**item_data)
            #item_query_ops = ItemQueryOps(mongo_db, mongo_session)
            #mongo_transaction_with_retry(mongo_session,lambda: item_query_ops.create(new_item))
        except PyMongoError as e:
            result_status = False
            result_msg = 'Database connection error. Please try again later!'
        except InvalidPrice as e:
            result_status = False
            result_msg = 'Price must be greater than 0 and correct form Ex:(9.99)'
        except InvalidName as e:
            result_status = False
            result_msg = 'Name can not be empty!'
        except InvalidUrl as e:
            result_status = False
            result_msg = 'Image url is not valid!'
        except Exception as e:
            print(e)
            result_status = False
            result_msg = str(e)

        if result_status:
            print("deneme5")
            return redirect('/')
        else:
            print("deneme6")
            session['result_msg'] = result_msg
            return redirect('/create_item')

# Continue with similar refactoring for other routes


@controller_bp.route('/item/<item>/review', methods=['GET','POST'])
@check_auth
def review(item):
    from app import (app, mongo_session, mongo_db, session, request, check_auth, check_admin)

    item_query_ops = ItemQueryOps(mongo_db, mongo_session)
    review_query_ops = ReviewQueryOps(mongo_db, mongo_session)
    reviews = mongo_transaction_with_retry(mongo_session,lambda: review_query_ops.search({'item': item}))
    user_old_review = mongo_transaction_with_retry(mongo_session,lambda: review_query_ops.find_one(session["username"], item))

    if request.method == 'GET':
        result_msg = session.pop("result_msg", "")
        item = mongo_transaction_with_retry(mongo_session,lambda: item_query_ops.get_by_name(item))
        return render_template('reviews.html', item=item, result_msg = result_msg, reviews = reviews, user_old_review=user_old_review)
    
    if request.method == 'POST':
        result_status = True
        result_msg = 'Review Added successfully!'
        user_query_ops = UserQueryOps(mongo_db, mongo_session)
        try:
            if user_old_review:
                user_old_review.rating = request.form.get('rating')
                user_old_review.review = request.form.get('review')
                mongo_transaction_with_retry(mongo_session,lambda: review_query_ops.update(user_old_review))
            else:
                new_review = Review(user=session['username'], 
                                    item=item, 
                                    rating=request.form.get('rating'), 
                                    review=request.form.get('review')
                                    )
                mongo_transaction_with_retry(mongo_session,lambda: review_query_ops.create(new_review))
            # Update avg rating for item and the user
            mongo_transaction_with_retry(mongo_session,lambda: item_query_ops.update_avg_rating(item_name = item, 
                                                                                    review_query_ops = review_query_ops))
            mongo_transaction_with_retry(mongo_session,lambda: user_query_ops.update_avg_rating(user_name = session['username'], 
                                                                                    review_query_ops = review_query_ops))

        except PyMongoError as e:
            result_status = False
            result_msg = 'Database connection error. Please try again later!'
        except LongTextError as e:
            result_status = False
            result_msg = 'Review can not be longer than 140 charachter!'
        except RangeError as e:
            result_status = False
            result_msg = 'Rating must be in range [1-5]'
        except Exception as e:
            result_status = False
            result_msg = str(e)
          
        if result_status == False: 
            session['result_msg'] = result_msg

        return redirect('/item/'+item+'/review')

def price_email(email_list, item_name, item_oldprice, item_newprice):
    
    
    try:
        sg = SendGridAPIClient('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')
        for mail in email_list:
            message = Mail(
            from_email='e2380533@ceng.metu.edu.tr',
            to_emails=mail,
            subject='Price Decrease',
            html_content=f'Price of the item {item_name} has decreased from {item_oldprice} to {item_newprice}'
            )
            response = sg.send(message)
        print(response.status_code)
    except Exception as e:
        print(str(e))

@controller_bp.route('/update_item/<name>', methods=['GET', 'POST'])
@check_auth
def update_item(name):
    from app import (mongo_session, mongo_db, session, request)
    
    try:
        # Retrieve the item from the database
        item_query_ops = ItemQueryOps(mongo_db, mongo_session)
        item = mongo_transaction_with_retry(mongo_session, lambda: item_query_ops.get_by_name(name))
        print("update2")

        if not item:
            return "Item not found", 404
        print(item)
        # Check if the logged-in user has permission to update the item
        if session['username'] != 'admin' and session['email'] != item.seller_mail:
            return "You don't have permission to update this item", 403

        if request.method == 'GET':
            return render_template('update_item.html', item=item)

        if request.method == 'POST':
            # Extract the form data for updating the item
            print("update3")
            users_with_item_as_favorite = mongo_db['user'].find({'favorite_list': name})

            form_data = {}
            form_data = {key: value for key, value in request.form.items() if value}
            
            # Validate the form data
            # You can add validation logic here
            create_item_params = CreateItemParams(**form_data)
            new_item = Item(**create_item_params.dict())
            new_itemprice= new_item.price
            old_itemprice = item.price
            #item_data = {k: v for k, v in create_item_params.dict().items() if v is not None and v != ''}
            #new_item = Item(**item_data)
            item_query_ops = ItemQueryOps(mongo_db, mongo_session)
            mongo_transaction_with_retry(mongo_session,lambda: item_query_ops.delete_by_name(name))

            mongo_transaction_with_retry(mongo_session,lambda: item_query_ops.create(new_item))
            if new_itemprice < old_itemprice:
                mail_list=[]
                for user in users_with_item_as_favorite:
                    mail_list.append(user['email'])
                price_email(mail_list, new_item.name, old_itemprice, new_itemprice)

            if(name!=new_item.name):
                for user in users_with_item_as_favorite:
                        user['favorite_list'].remove(name)
                        user['favorite_list'].append(new_item.name)
                        mongo_db['user'].update_one({'_id': user['_id']}, {'$set': {'favorite_list': user['favorite_list']}})
            return redirect(f'/item/{new_item.name}')
    
    except PyMongoError as e:
        return "Database connection error. Please try again later.", 500
    except InvalidPrice as e:
        return "Invalid price. Please enter a valid price.", 400
    except Exception as e:
        return str(e), 500



@controller_bp.route('/item/<name>', methods=['GET','POST'])
@check_auth
def item(name):
    from app import (app, mongo_session, mongo_db, session, request, check_auth, check_admin)

    if request.method == 'GET':
        user_query_ops = UserQueryOps(mongo_db, mongo_session)
        #user1 = User.query.filter_by(username=(session.get('username'))).first()
        user1= user_query_ops.get_by_username((session.get('username')))

        #session['phone']=user1.phone
        session['email']=user1.email
        favorite_list =user1.favorite_list
        print("deneme1")
        result_msg = session.pop("result_msg", "")
        item_query_ops = ItemQueryOps(mongo_db, mongo_session)
        item = mongo_transaction_with_retry(mongo_session,lambda: item_query_ops.get_by_name(name))
        if item.name in favorite_list:
            is_favorite=True
        else:
            is_favorite=False
        return render_template('item.html', item=item, result_msg = result_msg, is_favorite=is_favorite)

    if request.method == 'POST':
        
        print("deneme2")
        result_status = True
        result_msg = 'Item updated successfully!'
        try:    
            user_query_ops = UserQueryOps(mongo_db, mongo_session)

            #if request.args.get('delete') == 'true':
            if request.form.get('delete') == 'true':
                users_with_item_as_favorite = mongo_db['user'].find({'favorite_list': name})
                item_query_ops = ItemQueryOps(mongo_db, mongo_session)
                review_query_ops = ReviewQueryOps(mongo_db, mongo_session)
                mongo_transaction_with_retry(mongo_session,lambda: item_query_ops.delete_by_name(name))
                mongo_transaction_with_retry(mongo_session,lambda: review_query_ops.delete_item_reviews(name, user_query_ops))
                # Remove the item from users' favorite lists and update their documents
                for user in users_with_item_as_favorite:
                    user['favorite_list'].remove(name)
                    mongo_db['user'].update_one({'_id': user['_id']}, {'$set': {'favorite_list': user['favorite_list']}})
                return redirect('/')
            else:
                if 'add_to_favorite' in request.form:
                    user_query_ops.add_to_favorite_list(session['username'], name)
                    return redirect('/item/' + name)
                elif 'remove_from_favorite' in request.form:
                    user_query_ops.remove_from_favorite_list(session['username'], name)
                    return redirect('/item/' + name)
                else:
                    return redirect('/update_item/' + name)
            form_data = {}
            form_data = {key: value for key, value in request.form.items() if value}
            print("updateee")
            return redirect('/update_item/' + name)
            create_item_params = CreateItemParams(**form_data)
            # Create a new item with non-empty fields
            #new_item = Item(**create_item_params.dict())
            item_query_ops = ItemQueryOps(mongo_db, mongo_session)
            mongo_transaction_with_retry(mongo_session,lambda: item_query_ops.update_with_params(create_item_params))
            
        except PyMongoError as e:
            result_status = False
            result_msg = 'Database connection error. Please try again later!'
        except InvalidPrice as e:
            result_status = False
            result_msg = 'Price must be greater than 0 and correct form Ex:(9.99)'
        except Exception as e:
            result_status = False
            result_msg = str(e)
        
        if result_status == False:
            session['result_msg'] = result_msg

        return redirect('/item/' + name)



@controller_bp.route('/users/delete/<username>', methods=['POST'])
@check_admin
def users_delete(username): 
    from app import (app, mongo_session, mongo_db, session, request, check_auth, check_admin)

    result_status = True
    result_msg = 'User Deleted Successfully'
    try:
        user_query_ops = UserQueryOps(mongo_db, mongo_session)
        review_query_ops = ReviewQueryOps(mongo_db, mongo_session)
        item_query_ops = ItemQueryOps(mongo_db, mongo_session)
        user = mongo_db['user'].find_one({'username': username})

        
        # Delete items associated with the user's phone number
        #mongo_db['item'].delete_many({'seller_phone': user['phone']})
        
        # Delete items associated with the user's email address
        mongo_db['item'].delete_many({'seller_mail': user['email']})
        mongo_transaction_with_retry(mongo_session,lambda: user_query_ops.delete_by_username(username))
        mongo_transaction_with_retry(mongo_session,lambda: review_query_ops.delete_user_reviews(username, item_query_ops))

    except PyMongoError as e:
        result_status = False
        result_msg = 'Database connection error. Please try again later!'
    except Exception as e:
        result_status = False
        result_msg = str(e)

    if result_status == False:
        session['result_msg'] = result_msg

    return redirect('/users')

@controller_bp.route('/users/create', methods=['POST'])
@check_admin
def users_create():
    from app import mongo_db, mongo_session
    result_status = True
    result_msg = 'User Created Successfully'
    try:
        new_user = User(email=request.form.get("email"), 
                        username=request.form.get("username"), 
                        password=request.form.get("password")
                        )

        user_query_ops = UserQueryOps(mongo_db, mongo_session)
        mongo_transaction_with_retry(mongo_session,lambda: user_query_ops.create(new_user))
    except PyMongoError as e:
        result_status = False
        result_msg = 'Database connection error. Please try again later!'
    except Exception as e:
        result_status = False
        result_msg = str(e)

    if result_status == False:
        session['result_msg'] = result_msg

    return redirect('/users')

@controller_bp.route('/users', methods=['GET'])
@check_admin
def users_view():
    from app import (app, mongo_session, mongo_db, session, request, check_auth, check_admin)

    result_msg = session.pop("result_msg", "")
    user_query_ops = UserQueryOps(mongo_db, mongo_session)
    users = mongo_transaction_with_retry(mongo_session,lambda: user_query_ops.search({}))
    return render_template('users.html', result_msg = result_msg, users = users)

@controller_bp.route('/my_favorites')
@check_auth
def my_favorites():
    from app import (mongo_session, mongo_db, session)
    
    try:
        print("deneme11")
        user_query_ops = UserQueryOps(mongo_db, mongo_session)
        user = user_query_ops.get_by_username(session.get('username'))
        print("deneme22")
        if not user:
            return "User not found", 404
        print(user.favorite_list)
        #item_query_ops = ItemQueryOps(mongo_db, mongo_session)
        favorite_items = []
        for item_name in user.favorite_list:
            item = mongo_db['item'].find_one({'name': item_name})
            if item:
                print(item)
                favorite_items.append(item)
        return render_template('my_favorites.html', favorite_items=favorite_items)
    
    except PyMongoError as e:
        return "Database connection error. Please try again later.", 500
    except Exception as e:
        return str(e), 500

from pymongo.errors import PyMongoError

@controller_bp.route('/my_profile', methods=['GET', 'POST'])
@check_auth
def my_profile():
    from app import (mongo_session, mongo_db, session, request)
    
    if request.method == 'GET':
        # Retrieve the user's profile information from the database
        try:
            user = mongo_db['user'].find_one({'username': session['username']})
            if user:
                total_money = user.get('money', 0)  # Assuming total_money is stored in the user document
                favoritelist= user.get('favoritelist')
                total_damage=0
                if('1' in favoritelist):
                    total_damage+=1*favoritelist['1']
                if('2' in favoritelist):
                    total_damage+=5*favoritelist['2']
                if('3' in favoritelist):
                    total_damage+=10*favoritelist['3']
                if('4' in favoritelist):
                    total_damage+=50*favoritelist['4']
                if('5' in favoritelist):
                    total_damage+=200*favoritelist['5']
                if('6' in favoritelist):
                    total_damage+=500*favoritelist['6']
                if('7' in favoritelist):
                    total_damage+=2000*favoritelist['7']
                if('8' in favoritelist):
                    total_damage+=5000*favoritelist['8']
                if('9' in favoritelist):
                    total_damage+=10000*favoritelist['9']
                if('10' in favoritelist):
                    total_damage+=100000*favoritelist['10']
                
                
                
                return render_template('my_profile.html', user=user, total_money=total_money, total_damage=total_damage)
            else:
                return "User not found", 404
        except PyMongoError as e:
            return "An error occurred while retrieving the user's profile: " + str(e), 500
    
    elif request.method == 'POST':
        try:
            # Update user profile information
            email = request.form.get('email')
            #phone = request.form.get('phone')

            mongo_db['user'].update_one({'username': session['username']}, {'$set': {'email': email}})
            
            # Optionally, update the session data with the new information
            session['email'] = email
            #session['phone'] = phone

            return redirect('/my_profile')
        except PyMongoError as e:
            return "An error occurred while updating the profile: " + str(e), 500

@controller_bp.route('/collect_damage', methods=['POST'])
def collect_damage():
    from app import (mongo_session, mongo_db, session, request)

    data = request.get_json()
    total_damage = data.get('totalDamage')
    user = mongo_db['user'].find_one({'username': session['username']})
    

    # Assuming you have a function to update the user's money in the database
    if user:
        user_money= user.get('money')
        user_money+=total_damage
        mongo_db['user'].update_one({'username': session['username']}, {'$set': {'money': user_money}})
    if user:
        return jsonify({'success': True, 'newTotalMoney': user_money})
    else:
        return jsonify({'success': False})
    


@controller_bp.route('/add_to_favorites', methods=['POST'])
def add_to_favorites():
    from app import (mongo_session, mongo_db, session, request)

    if 'username' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'})

    data = request.json
    hero_name = data['heroName']
    hero_index = int(data['heroIndex'])
    username = session['username']

    update_result = mongo_db['user'].update_one(
        {'username': username},
        {'$inc': {f'favoritelist.{hero_index}': 1}}
    )

    if update_result.modified_count == 1:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Failed to add to favorites'})