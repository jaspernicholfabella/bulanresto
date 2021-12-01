import os
from flask import Flask,abort,url_for,render_template,request,redirect,g
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, form
from sqlalchemy import Column, Integer, String, Float, Text,DateTime, BLOB,desc,asc, Boolean
from flask_login import UserMixin, LoginManager, current_user, login_user, logout_user
from flask_admin.menu import MenuLink
from PIL import Image
from config import setup_app, config_data
from model import User,MenuItems,RestaurantSignup,Restaurants,Delivery
from view import RestaurantsModelView,MenuItemsModelView,UserModelView,RestaurantSignupModelView,DeliveryModelView,DeliveryModelView2
import random
import datetime

app = setup_app()
app.config['UPLOAD_FOLDER'] = config_data["upload_folder"]
app.config['MAX_CONTENT_PATH'] = config_data["max_upload_size"]

db = SQLAlchemy(app)
login = LoginManager(app)
cart_data = []
user_details = {}


admin = Admin(app, name=config_data["app_admin_name"], template_mode=config_data["app_admin_template_mode"])
admin.add_view(RestaurantsModelView(Restaurants, db.session))
admin.add_view(MenuItemsModelView(MenuItems, db.session))
admin.add_view(RestaurantSignupModelView(RestaurantSignup,db.session, name='Restaurant Account Requests'))
admin.add_view(UserModelView(User, db.session))
admin.add_view(DeliveryModelView(Delivery, db.session, name="Delivery Request"))
admin.add_view(DeliveryModelView2(Delivery, db.session, name="Delivery Record", endpoint='record'))
admin.add_link(MenuLink(name='Logout', category='', url="/logout"))


@login.user_loader
def load_user(user_id):
    return User.query.get(user_id)

## create database
@app.cli.command('db_create')
def db_create():
    db.create_all()
    print('Database created!')

## deleting database data
@app.cli.command('db_drop')
def db_drop():
    db.drop_all()
    print('Database dropped!')


## ROUTES
@app.route('/')
def home():
    return redirect(url_for("login"))

@app.route('/homepage')
def homepage():
    if current_user.is_authenticated:
        if current_user.access == 'user':
            menu_items = MenuItems.query.all()
            random_menu_1 = menu_items[random.randrange(0,len(menu_items))]
            random_menu_2 = menu_items[random.randrange(0,len(menu_items))]
            return render_template('index.html', random_menu=[random_menu_1, random_menu_2])
    else:
        return config_data["access_deny_message"]

@app.route('/restosignup')
def restosignup():
    error = False
    return render_template("restosignup.html",error=error)

@app.route('/signup')
def signup():
    error = False
    return render_template("signup.html",error=error)

@app.route('/login')
def login(error=False):
    return render_template("login.html",error=error)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/validatelogin',methods=["POST","GET"])
def validatelogin():
    if request.method == "POST":
        username=request.form["username"]
        password=request.form["password"]
        user = User.query.filter_by(username=username).one()
        if ((username == user.username) and (password == user.password)):
            login_user(user)
            user_details = {}
            user_details.update({'id':user.id})
            user_details.update({'name': user.name})
            user_details.update({'access': user.access})
            if user.access == 'user':
                return redirect(url_for("homepage"))
            elif user.access == 'restaurant':
                return redirect(url_for("admin.index"))
            elif user.access == 'admin':
                return redirect(url_for("admin.index"))
    return f'{username},{password}'

@app.route('/validatesignup', methods=["POST","GET"])
def validatesignup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        homeaddress = request.form['homeaddress']
        password = request.form['password']
        rpassword = request.form['rpassword']

        if User.query.filter_by(username=username).count() > 0:
            return render_template("request_submitted.html", message=f"username:{username} already in use.")
        elif User.query.filter_by(emailaddress=email).count() > 0:
            return render_template("request_submitted.html", message=f"email:{email} already in use.")
        elif password != rpassword:
            return render_template("request_submitted.html", message=f"Password does not match")
        else:
            add_signup = User(
                username=username,
                password=password,
                emailaddress=email,
                homeaddress = homeaddress,
                access='user'
            )
            db.session.add(add_signup)
            db.session.commit()
            return render_template("request_submitted.html", message=f"Signed Up Successfully")

    return 'error'

@app.route('/validaterestosignup',methods=["POST","GET"])
def validate_resto_signup():
    try:
        data_count = 0
        data_count = RestaurantSignup.query.count()

        if request.method == "POST":
            file = request.files["file"]
            print(f'filename: {file.filename}')
            final_file_name = f'{data_count}_{file.filename}'
            file.save(f"{config_data['upload_folder']}\\{final_file_name}")
            new_restaurant_request = RestaurantSignup(
                name=request.form["name"],
                owner=request.form["owner"],
                address=request.form["address"],
                email=request.form["email"],
                attached_files=final_file_name,
                date=datetime.datetime.now()
            )
            db.session.add(new_restaurant_request)
            db.session.commit()
            return render_template("request_submitted.html",message=f"Request Submitted! {data_count}")
    except Exception as e:
        return render_template("request_submitted.html",message=f"Request Failed! : {e}")

@app.route('/restaurant_list')
def restaurant_list():
    if current_user.is_authenticated:
        if current_user.access == 'user':
            restaurant_list = Restaurants.query.order_by(asc(Restaurants.title))
            filtered_restaurant_list = []
            for restaurant in restaurant_list:
                filtered_restaurant_list.append(restaurant)
            return render_template('restaurant_list.html', restaurant_list=filtered_restaurant_list)
    else:
        return config_data["access_deny_message"]

@app.route('/restaurant/<string:slug>')
def restaurantpage(slug):
    if current_user.is_authenticated:
        if current_user.access == 'user':
            cart_data.clear()
            restaurant = Restaurants.query.filter_by(slug=slug).one()
            menu_items = MenuItems.query.filter_by(slug=slug).order_by(asc(MenuItems.name))
            return render_template('restaurant.html', restaurant=restaurant, menu_items=menu_items,cart_data_len=0)
    else:
        return config_data["access_deny_message"]

@app.route('/addtocart',methods=["POST","GET"])
def addtocart():
    try:
        if request.method == "POST":
            id = int(request.form["submit_button"])
            test_q = MenuItems.query.filter_by(id=id).first()
            slug = test_q.slug
            cart_data.append(id)
            print(f'cart_data: {cart_data}')
            restaurant = Restaurants.query.filter_by(slug=slug).one()
            menu_items = MenuItems.query.filter_by(slug=slug).order_by(asc(MenuItems.name))
            return render_template('restaurant.html', restaurant=restaurant, menu_items=menu_items,cart_data_len=len(cart_data))

    except Exception as e:
        return f'Error: {e}'

@app.route('/cart/<string:slug>')
def cart(slug):
    tempdict = {i:cart_data.count(i) for i in cart_data}
    cart_data_list=[]
    for k,v in tempdict.items():
        menu_items = MenuItems.query.filter_by(id=int(k)).first()
        cart_data_list.append({
            'name' : menu_items.name,
            'amount' : v,
            'price' : int(str(menu_items.price).replace('PHP','').strip())
        })
    return render_template("cart.html",cart_data_list=cart_data_list,slug=slug)

@app.route('/order/<string:order_data>',methods=["POST","GET"])
def order(order_data):
    try:
        if request.method == "POST":
            id = current_user.id
            address = current_user.homeaddress
            slug = request.form['slug']
            total = request.form['total']
            new_order_data = order_data
            new_order = Delivery(
                userid=id,
                slug=slug,
                cartitems=new_order_data,
                address=address,
                date=datetime.datetime.now(),
                total=total
            )
            db.session.add(new_order)
            db.session.commit()
            cart_data = []
            return render_template("message_feedback.html", message=f"The order has been submitted, wait for it to be delivered Enjoy! :)")
    except Exception as e:
        return render_template("message_feedback.html", message=f"Error {e}")

@app.route('/search',methods=["POST","GET"])
def searchpage():
    if current_user.is_authenticated:
        if current_user.access == 'user':
            if request.method == "POST":
                search = request.form["search_input"]
                return redirect(url_for("searchresults", search=search))
            else:
                return render_template("search.html")
    else:
        return config_data["access_deny_message"]

@app.route('/results/<search>')
def searchresults(search):
    if current_user.is_authenticated:
        if current_user.access == 'user':
            menu_items = MenuItems.query.order_by(asc(MenuItems.name))
            filtered_menu_items = []
            for menu in menu_items:
                if search.lower() in menu.search_tags:
                    filtered_menu_items.append(menu)

            return render_template('results.html', menu_items=filtered_menu_items)
    else:
        return config_data["access_deny_message"]


if __name__ == "__main__":
    app.run(debug=True)


