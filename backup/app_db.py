import os
from flask import Flask,render_template,abort,url_for,render_template,request,redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float, Text, BLOB,desc,asc, DateTime, Boolean
from flask_admin import Admin, form
from flask_admin.contrib.sqla import ModelView
from flask_login import UserMixin, LoginManager, current_user, login_user, logout_user
from flask_admin.menu import MenuLink
from flask_admin.contrib.sqla.fields import QuerySelectField
from flask_admin.contrib import fileadmin
from jinja2 import Markup
from PIL import Image
from wtforms import SelectField,StringField,SubmitField
from wtforms.validators import DataRequired
import random

app = Flask(__name__)

##setting up SQLAlchemy
basedir = os.getcwd() ## the path for the application itself
file_path = os.path.join(basedir,'static/images')

##config for SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'bulan.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'mysecretkey'
app.config['FLASK_ADMIN_SWATCH'] = 'superhero'
app.config['UPLOAD_FOLDER'] = os.path.join(basedir,'static/uploads')

db = SQLAlchemy(app)
admin = Admin(app,name='Bulan Restaurant Portal Admin',template_mode='bootstrap3')
login = LoginManager(app)

user_details={}


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
def homepage():
    menu_items = MenuItems.query.all()
    random_menu_1 = menu_items[random.randrange(0,len(menu_items))]
    random_menu_2 = menu_items[random.randrange(0,len(menu_items))]

    return render_template('index.html',random_menu=[random_menu_1,random_menu_2])

@app.route('/restosignup')
def signup():
    error = False
    return render_template("signup.html",error=error)


@app.route('/login')
def login():
    error = False
    return render_template("login.html",error=error)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('homepage'))

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


@app.route('/restaurant/<string:slug>')
def restaurantpage(slug):
    restaurant = Restaurants.query.filter_by(slug=slug).one()
    menu_items = MenuItems.query.filter_by(slug=slug).order_by(asc(MenuItems.name))
    return render_template('restaurant.html',restaurant=restaurant,menu_items=menu_items)

@app.route('/search',methods=["POST","GET"])
def searchpage():
    if request.method == "POST":
        search = request.form["search_input"]
        return redirect(url_for("searchresults",search=search))
    else:
        return render_template("search.html")

@app.route('/results/<search>')
def searchresults(search):
    # return f"<h1>{search}</h1>"
    menu_items = MenuItems.query.order_by(asc(MenuItems.name))
    filtered_menu_items = []
    for menu in menu_items:
        if search.lower() in menu.search_tags:
            filtered_menu_items.append(menu)

    return render_template('results.html',menu_items=filtered_menu_items)



## Database Class
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = Column(db.Integer, primary_key=True)
    username = Column(String,unique=True)
    password = Column(String)
    name = Column(String)
    emailaddress = Column(String)
    access = Column(String)

class RestaurantSignup(db.Model):
    __tablename__ = 'restaurantsignup'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    address = Column(String(255))
    owner = Column(String(255))
    email = Column(String(255))
    attached_files = Column(String(255))
    date = Column(DateTime)
    approved = Column(Boolean,default=False)


class Restaurants(db.Model):
    __tablename__ = 'restaurants'
    id = Column(Integer,primary_key=True)
    title = Column(String(255))
    subtitle = Column(Text)
    image = Column(String(255))
    slug = Column(String(255))
    useraccount = Column(String(255))



class MenuItems(db.Model):
    __tablename__ = 'menu_items'
    id = Column(Integer,primary_key=True)
    name = Column(String(255))
    details = Column(String(255))
    image = Column(String(255))
    price = Column(String(255))
    search_tags = Column(String(255))
    slug = Column(String(255))


class Delivery(db.Model):
    __tablename__ = 'delivery'
    id = Column(Integer,primary_key=True)
    userid = Column(Integer),
    slug = Column(String),
    cartitems=Column(String),
    date = Column(DateTime)
    total = Column(Float)
    delivered = Column(Boolean,default=False)


class UserModalView(ModelView):
    can_delete = False
    page_size = 50
    create_modal = True
    edit_modal=True

    l1 = ['user','restaurant','admin']
    l2 = []
    for i in range(0, len(l1)):
        l2.append((l1[i], l1[i]))
    form_choices = {
        'access': l2
    }

    def is_accessible(self):
        if current_user.is_authenticated :
            if current_user.access == 'admin':
                return True

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))
        return True

class RestaurantsModalView(ModelView):
    can_delete=False
    page_size = 50
    create_modal = True
    edit_modal = True

    # column_exclude_list = ['content',]
    form_excluded_columns=['slug',]

    def on_model_change(self, form, model, is_created):
        if is_created and not model.slug:
            model.slug = str(model.useraccount)


    def _list_thumbnail(view, context, model, name):
        if name == 'image':
            return model.image
        else:
            return ''
    column_formatters = {
        'image': _list_thumbnail,
    }
    form_extra_fields = {
        'image': form.ImageUploadField('Image', base_path=file_path, thumbnail_size=(100, 100, True)),
    }

    def is_accessible(self):
        if current_user.is_authenticated:
            if current_user.access == 'admin':
                return True

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))
        return True

class MenuItemsModalView(ModelView):
    # can_delete=False
    page_size = 50
    create_modal = True
    edit_modal = True
    # column_exclude_list = ['slug',]
    form_excluded_columns=['slug',]

    def _list_thumbnail(view, context, model, name):
        if name == 'image':
            return model.image
        else:
            return ''

    column_formatters = {
        'image': _list_thumbnail,
    }
    form_extra_fields = {
        'image': form.ImageUploadField('Image', base_path=file_path, thumbnail_size=(100, 100, True)),
    }

    def on_model_change(self, form, model, is_created):
        if is_created and not model.slug:
            model.slug = str(current_user.name)

    def get_query(self):
        return self.session.query(self.model).filter(self.model.slug == current_user.name)

    def is_accessible(self):
        if current_user.is_authenticated :
            if current_user.access == 'restaurant':
                return True

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))
        return True

class RestaurantSignupModelView(ModelView):
    can_create=False
    can_delete=False
    page_size = 50
    create_modal = True
    edit_modal = True

    def get_query(self):
        return self.session.query(self.model).filter(self.model.approved == False)

    def is_accessible(self):
        if current_user.is_authenticated :
            if current_user.access == 'admin':
                return True

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))
        return True

class DeliveryModelView(ModelView):
    can_create=False
    can_delete=False
    page_size = 50
    create_modal = True
    edit_modal = True
    form_excluded_columns=['userid','slug','cartitems''date','total']

    def get_query(self):
        return self.session.query(self.model).filter(self.model.approved == False)

    def is_accessible(self):
        if current_user.is_authenticated :
            if current_user.access == 'restaurant':
                return True

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))
        return True

admin.add_view(RestaurantsModalView(Restaurants, db.session))
admin.add_view(MenuItemsModalView(MenuItems,db.session))
admin.add_view(UserModalView(User,db.session))
admin.add_link(MenuLink(name='Logout', category='', url="/logout"))
admin.add_view(RestaurantSignupModelView(RestaurantSignup,db.session))
admin.add_view(DeliveryModelView(Delivery, db.session, name="Testing"))

if __name__ == "__main__":
    app.run(debug=True)


