import os
from flask import Flask,abort,url_for,render_template,request,redirect,g
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, form
from sqlalchemy import Column, Integer, String, Float, Text,DateTime, BLOB,desc,asc, Boolean,func
from flask_login import UserMixin, LoginManager, current_user, login_user, logout_user
from flask_admin.menu import MenuLink
from flask_admin import AdminIndexView, expose
from PIL import Image
from config import setup_app, config_data
from model import User,MenuItems,RestaurantSignup,Restaurants,Delivery,Feedback,CartRecord,ReservationSetup,Reservations
from view import RestaurantsModelView,MenuItemsModelView,UserModelView,RestaurantSignupModelView,DeliveryModelView,DeliveryModelView2,ReservationSetupModelView,ReservationModelView
import random
import datetime
from forms import SignupForm,LoginForm,RestaurantSignupForm,SearchForm,FeedbackForm,CartForm,ReservationForm,DateRangeForm
from reservation_setup import setup_reservations
from dateutil.relativedelta import relativedelta

app = setup_app()
app.config['UPLOAD_FOLDER'] = config_data["upload_folder"]
app.config['MAX_CONTENT_PATH'] = config_data["max_upload_size"]

db = SQLAlchemy(app)
login = LoginManager(app)
user_details = {}
global current_slug
current_slug=''

class HomeView(AdminIndexView):
    search_menu = []

    def most_frequent(self,List):
        return max(set(List), key=List.count)

    def add_search_menu(self,str1):
        str2 = str1.split('__')
        temp = []
        for str in str2:
            temp.append(''.join([i for i in str if i.isalpha() or i.isspace()]))

        for s in list(filter(None, temp)):
            self.search_menu.append(s)

    @expose('/',methods=['GET','POST'])
    def index(self):
        if current_user.is_authenticated:
            if current_user.access == 'admin':
                total_no = []
                total_no.append(User.query.count())
                total_no.append(Restaurants.query.count())
                total_no.append(RestaurantSignup.query.filter_by(approved=False).count())
                return self.render('admin/index.html',total_no = total_no,is_admin=True )

            elif current_user.access == 'restaurant':
                total_no = []

                #top menu item this month 0
                temp_date_from = datetime.date.today().replace(day=1)
                temp_date_to = datetime.date.today() + relativedelta(months=+1)
                delivery_month = Delivery.query.filter(Delivery.date >= temp_date_from).filter(Delivery.date < temp_date_to).filter_by(delivered=True).filter_by(slug=current_user.name)
                self.search_menu = []
                for delivered in delivery_month:
                    self.add_search_menu(delivered.cartitems)
                try:
                    total_no.append(self.most_frequent(self.search_menu))
                except:
                    total_no.append('No Data Yet')

                #top menu item of all time 1
                delivery = Delivery.query.filter_by(delivered=True).filter_by(slug=current_user.name)
                self.search_menu=[]
                for delivered in delivery:
                    self.add_search_menu(delivered.cartitems)
                try:
                    total_no.append(self.most_frequent(self.search_menu))
                except:
                    total_no.append('No Data Yet')

                #Delivery Requests 2
                total_no.append(Delivery.query.filter_by(delivered=False).filter_by(slug=current_user.name).count())
                #Food Delivered Today 3
                total_no.append(Delivery.query.filter(
                    func.date(Delivery.date) == datetime.date.today()
                ).filter_by(delivered=True).filter_by(slug=current_user.name).count())
                #Food Delivered This Month 4
                total_no.append(
                Delivery.query.filter(Delivery.date >= temp_date_from)\
                    .filter(Delivery.date < temp_date_to)\
                    .filter_by(delivered=True).filter_by(slug=current_user.name).count())
                #total food Delivered 5
                total_no.append(Delivery.query.filter_by(delivered=True).filter_by(slug=current_user.name).count())

                #reservations today 6
                total_no.append(Reservations.query.filter(
                    func.date(Reservations.reservation_date_and_time) == datetime.date.today()
                ).filter_by(slug=current_user.name).count())

                #reservations this month 7
                total_no.append(Reservations.query.filter(Reservations.reservation_date_and_time >= temp_date_from)\
                                .filter(Reservations.reservation_date_and_time < temp_date_to)
                                .filter_by(slug=current_user.name).count())

                #all reservations 8
                total_no.append(Reservations.query.filter_by(slug=current_user.name).count())

                form = DateRangeForm()

                if form.validate_on_submit():
                    #2021-12-01 2022-01-31
                    temp_date_from = datetime.datetime.strptime(form.date_from.data,'%Y-%m-%d')
                    temp_date_to = datetime.datetime.strptime(form.date_to.data,'%Y-%m-%d')
                    no_product = 0
                    food_delivery = 0
                    delivery = Delivery.query.filter(Delivery.date >= temp_date_from)\
                                .filter(Delivery.date < temp_date_to).filter_by(delivered=True).filter_by(slug=current_user.name)
                    self.search_menu = []

                    for delivered in delivery:
                        self.add_search_menu(delivered.cartitems)
                        cartitems_ar = delivered.cartitems.split('::')
                        cartitems_ar = [x for x in cartitems_ar if x]
                        for item in cartitems_ar:
                            no_product += int(item.split('__')[1])

                    try:
                        top_menu_item = self.most_frequent(self.search_menu)
                        food_delivery = len(self.search_menu)
                    except:
                        top_menu_item = 'No Data Yet'

                    # reservations today 6
                    reservations = Reservations.query.filter(Reservations.reservation_date_and_time >= temp_date_from)\
                                .filter(Reservations.reservation_date_and_time < temp_date_to).filter_by(slug=current_user.name).count()

                    delivery_record = Delivery.query.filter(Delivery.date >= temp_date_from)\
                                .filter(Delivery.date < temp_date_to).filter_by(delivered=True).filter_by(slug=current_user.name)

                    total_sales = 0
                    for delivery in delivery_record:
                        total_sales += delivery.total

                    return self.render('admin/records.html',
                                       type='',
                                       top_menu_item=top_menu_item,
                                       no_product=no_product,
                                       food_delivery=food_delivery,
                                       reservations=reservations,
                                       delivery_record=delivery_record,
                                       total_sales=total_sales,
                                       date_range = f'{temp_date_from.strftime("%b %d, %Y")} - {temp_date_to.strftime("%b %d, %Y")}'
                                       )




                return self.render('admin/index.html',total_no=total_no, is_admin=False,form=form)

    @expose('/records/<string:type>')
    def records(self,type):
        if current_user.is_authenticated:
            if current_user.access == 'restaurant':
                if type == 'daily':
                    #top menu item this month 0
                    no_product = 0
                    food_delivery = 0
                    delivery = Delivery.query.filter(
                        func.date(Delivery.date) == datetime.date.today()
                    ).filter_by(delivered=True).filter_by(slug=current_user.name)
                    self.search_menu = []

                    for delivered in delivery:
                        self.add_search_menu(delivered.cartitems)
                        cartitems_ar = delivered.cartitems.split('::')
                        cartitems_ar = [x for x in cartitems_ar if x]
                        for item in cartitems_ar:
                            no_product += int(item.split('__')[1])

                    try:
                        top_menu_item = self.most_frequent(self.search_menu)
                        food_delivery = len(self.search_menu)
                    except:
                        top_menu_item = 'No Data Yet'

                    #reservations today 6
                    reservations = Reservations.query.filter(
                        func.date(Reservations.reservation_date_and_time) == datetime.date.today()
                    ).filter_by(slug=current_user.name).count()

                    delivery_record = Delivery.query.filter(
                        func.date(Delivery.date) == datetime.date.today()
                    ).filter_by(delivered=True).filter_by(slug=current_user.name)

                    total_sales = 0
                    for delivery in delivery_record:
                        total_sales += delivery.total


                elif type == "all":
                    # top menu item this month 0
                    no_product = 0
                    food_delivery = 0
                    delivery = Delivery.query.filter_by(delivered=True).filter_by(slug=current_user.name)
                    self.search_menu = []

                    for delivered in delivery:
                        self.add_search_menu(delivered.cartitems)
                        cartitems_ar = delivered.cartitems.split('::')
                        cartitems_ar = [x for x in cartitems_ar if x]
                        for item in cartitems_ar:
                            no_product += int(item.split('__')[1])

                    try:
                        top_menu_item = self.most_frequent(self.search_menu)
                        food_delivery = len(self.search_menu)
                    except:
                        top_menu_item = 'No Data Yet'

                    # reservations today 6
                    reservations = Reservations.query.filter_by(slug=current_user.name).count()

                    delivery_record = Delivery.query.filter_by(delivered=True).filter_by(slug=current_user.name)

                    total_sales = 0
                    for delivery in delivery_record:
                        total_sales += delivery.total


                return self.render('admin/records.html',
                                   type=type,
                                   top_menu_item=top_menu_item,
                                   no_product = no_product,
                                   food_delivery=food_delivery,
                                   reservations=reservations,
                                   delivery_record=delivery_record,
                                   total_sales = total_sales,
                                   date_range=''
                                   )



admin = Admin(app, index_view=HomeView(), template_mode=config_data["app_admin_template_mode"])
admin.add_view(ReservationSetupModelView(ReservationSetup,db.session, name='Reservation Setup'))
admin.add_view(RestaurantsModelView(Restaurants, db.session))
admin.add_view(MenuItemsModelView(MenuItems, db.session))
admin.add_view(RestaurantSignupModelView(RestaurantSignup,db.session, name='Restaurant Account Requests'))
admin.add_view(UserModelView(User, db.session))
admin.add_view(ReservationModelView(Reservations,db.session))
admin.add_view(DeliveryModelView(Delivery, db.session, name="Delivery Request"))
admin.add_view(DeliveryModelView2(Delivery, db.session, name="Delivery Record", endpoint='record'))
admin.add_link(MenuLink(name='Logout', category='', url="/logout"))



@app.context_processor
def default_contents():
    home_title = 'Life is full of Memories, we make them sweeter'
    home_subtitle = 'Choose a Restaurant'
    home_card_title = ["Restaurant Reservations","Order Food Now!","Join our Community"]
    home_card_subtitle =["Reserve a seat on our affiliated restaurants.","Easy ordering with free shipping fee.","We listen to feedback, be a part of our community."]
    restaurant_list_title = 'Our Affiliated Restaurant\'s'
    return dict(home_title=home_title,
                home_subtitle= home_subtitle,
                home_card_title = home_card_title,
                home_card_subtitle=home_card_subtitle,
                restaurant_list_title=restaurant_list_title)

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

class ReservationSetup(db.Model):
    __tablename__ = 'reservation_setup'
    id = Column(Integer,primary_key=True)
    option_update = Column(String)
    business_hours_start= Column(String)
    business_hours_end= Column(String)
    gap_in_minutes = Column(Integer,default=60)
    skip_weekends = Column(Boolean,default=False)
    slug=Column(String)
    table_slots = Column(Integer,default=1)

def empty_cart_data():
    global current_slug
    current_slug = ''
    num_rows_deleted = db.session.query(CartRecord).delete()
    db.session.commit()

## ROUTES
@app.route('/')
def home():
    is_login = False
    if current_user.is_authenticated:
        if current_user.access == 'user':
            empty_cart_data()
            is_login = True


    restaurant = Restaurants.query.all()
    random_number_1 = random.randrange(0, len(restaurant))
    random_number_2 = random.randrange(0, len(restaurant))
    random_resto_1 = restaurant[random_number_1]
    random_resto_2 = restaurant[random_number_2]
    menu_item_1 = MenuItems.query.filter_by(slug=random_resto_1.slug).all()
    menu_item_2 = MenuItems.query.filter_by(slug=random_resto_2.slug).all()

    return render_template('index.html',random_resto=[random_resto_1,random_resto_2],menu_item =[menu_item_1,menu_item_2],is_login=is_login)


@app.route('/reservation/<string:slug>',methods=["POST","GET"])
def reservation(slug):
    try:
        if current_user.is_authenticated:
            if current_user.access == 'user':
                restaurant = Restaurants.query.filter_by(slug=slug).one()
                reservation = ReservationSetup.query.filter_by(slug=slug).one()
                reservation_month_day,reservation_hours =setup_reservations(
                    option_update=reservation.option_update,
                    skip_weekends=reservation.skip_weekends,
                    business_hours_start_string=reservation.business_hours_start,
                    business_hours_end_string=reservation.business_hours_end,
                    gap_in_minutes=reservation.gap_in_minutes
                )
                form = ReservationForm()

                if form.validate_on_submit():
                    # User.query.filter_by(username=form.user_name.data).count()
                    date_selected = f'{form.month.data} {form.day.data}, {datetime.datetime.now().year}'

                    time_slots = {}
                    for i in range(0,len(reservation_hours) - 1):
                        date_selected_dt = datetime.datetime.strptime(f'{str(form.month.data)[:3]} {form.day.data} {datetime.datetime.now().year} {reservation_hours[i]}','%b %d %Y %I:%M %p')
                        slot_for_the_day = Reservations.query.filter_by(reservation_date_and_time=date_selected_dt).filter_by(slug=slug).count()
                        slot_available = reservation.table_slots - slot_for_the_day

                        if slot_available > 0:
                            time_slots.update({f'{str(reservation_hours[i]).replace(" ","")} - {str(reservation_hours[i+1]).replace(" ","")}':slot_available})

                    return render_template('reservation.html',
                                           restaurant=restaurant,
                                           time_slots=time_slots,
                                           reservation_month_day=reservation_month_day,
                                           form=form,
                                           date_selected = date_selected,
                                           show_data=True)

                return render_template('reservation.html',
                                       restaurant=restaurant,
                                       reservation_month_day=reservation_month_day,
                                       form=form,
                                       show_data=False)
        else:
            return render_template("messages.html",no_button=False, message_title=f"REQUEST DENIED.", message_subtitle=f"Login First",is_error=True)
    except Exception as e:
        return render_template("messages.html", no_button=True, message_title=f"REQUEST DENIED. No Reservations as of this moment",
                               message_subtitle=f"Error: {e}", is_error=True)
    return render_template("messages.html",no_button=False, message_title=f"REQUEST DENIED.", message_subtitle=f"Login First",is_error=True)

@app.route('/reserve/<string:slug>/<string:date_time_slot>')
def reserve(slug,date_time_slot):
    if current_user.is_authenticated:
        if current_user.access == 'user':
            try:
                time=date_time_slot.split('-')[0].strip()
                date = date_time_slot.split('-')[2].strip()
                month = date.split(' ')[0][:3].lower()
                day = date.split(' ')[1].replace(',','').strip()
                year = date.split(' ')[2].strip()
                date = datetime.datetime.strptime(f'{month} {day} {year} {time}','%b %d %Y %I:%M%p')

                reserve = Reservations(
                    customer_username=current_user.username,
                    reservation_date_and_time=date,
                    date_reserved=datetime.datetime.now(),
                    slug=slug
                )

                db.session.add(reserve)
                db.session.commit()
                return redirect(url_for('reservation_success'))
            except Exception as e:
                return str(e)
        else:
            return render_template("messages.html",no_button=False, message_title=f"REQUEST DENIED.", message_subtitle=f"Login First",is_error=True)
    return redirect(url_for('reservation_success'))

@app.route('/signup',methods=["POST","GET"])
def signup():
    is_error=True
    error=''
    is_login = False
    if current_user.is_authenticated:
        if current_user.access == 'user':
            is_login = True
    form = SignupForm()
    if form.validate_on_submit():
        try:
            if User.query.filter_by(username=form.user_name.data).count() > 0:
                return render_template("messages.html",no_buttons=False, message_title=f"REQUEST DENIED.", message_subtitle=f"Username {form.user_name.data} is already on the database.",is_error=is_error)
            elif User.query.filter_by(emailaddress=form.email_address.data).count() > 0:
                return render_template("messages.html",no_buttons=False, message_title=f"REQUEST DENIED.", message_subtitle=f"Email Address {form.email_address.data} is already on the database.",is_error=is_error)
            else:
                add_signup = User(
                    username=form.user_name.data,
                    password=form.password.data,
                    emailaddress=form.email_address.data,
                    homeaddress=form.home_address.data,
                    access='user'
                )
                db.session.add(add_signup)
                db.session.commit()
                is_error=False
                return render_template("messages.html",no_button=False,  message_title=f"REQUEST ACCEPTED.", message_subtitle="Your Account is created Successfuly.",is_error=is_error)

        except Exception as e:
            error = f'Something Went Wrong! {e}'
            return render_template("messages.html",no_button=False,  message_title=f"SOMETHING WENT WRONG!", message_subtitle=f"{e}",is_error=is_error)

    return render_template("signup.html",form=form,error=error)

@app.route('/login',methods=["POST","GET"])
def login():
    error=''
    is_login = False
    if current_user.is_authenticated:
        if current_user.access == 'user':
            is_login = True
    form=LoginForm()
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(username=form.user_name.data).one()
            if form.user_name.data == user.username and form.password.data == user.password:
                login_user(user)
                user_details = {}
                user_details.update({'id': user.id})
                user_details.update({'name': user.name})
                user_details.update({'access': user.access})
                if user.access == 'user':
                    return redirect(url_for("home"),)
                elif user.access == 'restaurant':
                    total_no = []
                    return redirect(url_for("admin.index"))
                elif user.access == 'admin':
                    total_no = []
                    total_no.append(User.query.count())
                    total_no.append(Restaurants.query.count())
                    total_no.append(RestaurantSignup.query.count())
                    return redirect(url_for("admin.index"))
            else:
                error = 'Username or Password is Incorrect'
                return render_template("login.html", form=form, error=error)
        except Exception as e:
            error = 'Username or Password is Incorrect'
            return render_template("login.html", form=form, error=error)
    return render_template("login.html", form=form, error=error)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/restosignup',methods=["POST","GET"])
def restosignup():
    form = RestaurantSignupForm()
    data_count = 0
    try:
        data_count = RestaurantSignup.query.count()
    except:
        pass
    if form.validate_on_submit():
        is_error = True
        try:
            final_file_name = f'{data_count}_{form.file_field.data.filename}'
            form.file_field.data.save(f"{config_data['upload_folder']}\\{final_file_name}")
            new_restaurant_request = RestaurantSignup(
                name=form.restaurant_name.data,
                owner=form.owner_name.data,
                address=form.address.data,
                email=form.email_address.data,
                attached_files=final_file_name,
                date=datetime.datetime.now()
            )
            db.session.add(new_restaurant_request)
            db.session.commit()
            is_error=False
            return render_template("messages.html",no_button=False, message_title=f"REQUEST ACCEPTED.", message_subtitle="Your Message has been submitted. Wait for email from the admin for your username and password if your request is accepted.",is_error=is_error)
        except Exception as e:
            return render_template("messages.html",no_button=False, message_title=f"ERROR IN REQUEST!", message_subtitle="An Unknown Error Has Occured",is_error=is_error)

    return render_template("restosignup.html", form=form)

@app.route('/search',methods=["POST","GET"])
def searchpage():

    form = SearchForm()
    is_login = False
    if current_user.is_authenticated:
        if current_user.access == 'user':
            empty_cart_data()
            is_login = True
    is_result_empty = True
    menu_items = []
    if form.validate_on_submit():
        menu_items = MenuItems.query.order_by(asc(MenuItems.name))
        filtered_menu_items = []
        for menu in menu_items:
            if str(form.search_string.data).lower() in menu.search_tags:
                filtered_menu_items.append(menu)
        is_result_empty=False
        if len(filtered_menu_items) == 0:
            is_result_empty=True
        return render_template("search.html", form=form, menu_items=filtered_menu_items, is_result_empty=is_result_empty,is_login=is_login)
    else:
        return render_template("search.html",form=form,menu_items=menu_items,is_result_empty=is_result_empty,is_login=is_login)

    return render_template("search.html",form=form,menu_items=menu_items,is_result_empty=is_result_empty,is_login=is_login)

@app.route('/restaurant_list')
def restaurant_list():
    empty_cart_data()
    is_login = False
    if current_user.is_authenticated:
        if current_user.access == 'user':
            empty_cart_data()
            is_login = True

    restaurant_list = Restaurants.query.order_by(asc(Restaurants.title))
    filtered_restaurant_list = []
    rate_dict = {}
    for restaurant in restaurant_list:
        total = 0
        i = 0
        feedback = Feedback.query.filter_by(slug=restaurant.slug)
        try:
            for f in feedback:
                total += f.rate
                i+=1
            av = total / i
            rate_dict.update({restaurant.slug:av})
        except:
            rate_dict.update({restaurant.slug:total})
        filtered_restaurant_list.append(restaurant)

    return render_template('restaurant_list.html', restaurant_list=filtered_restaurant_list,rate_dict=rate_dict,is_login=is_login)


@app.route('/restaurant/<string:slug>',methods=['GET','POST'])
def restaurantpage(slug):
    global current_slug
    form = FeedbackForm()
    cart_form = CartForm()

    is_login = False
    if current_user.is_authenticated:
        if current_user.access == 'user':
            is_login = True

            if form.validate_on_submit():
                if len(form.feedback_name.data) < 1:
                    name = current_user.name
                else:
                    name = form.feedback_name.data

                feedback_query = Feedback(
                    username=name,
                    slug=slug,
                    rate=float(form.rate.data),
                    comment=form.message.data
                )
                db.session.add(feedback_query)
                db.session.commit()
                return render_template("messages.html",no_button=True,message_title=f"COMMENT SUBMITTED!",
                                       message_subtitle="Your comment has been submitted", is_error=False)

            if current_slug != '':
                if (current_slug != slug):
                    current_slug == slug
                    num_rows_deleted = db.session.query(CartRecord).delete()
                    db.session.commit()
                else:
                    if cart_form.validate_on_submit():
                        add_cart_record = CartRecord(
                            menu_name=cart_form.menu_name.data,
                            slug = slug,
                            price = float(cart_form.price.data))
                        db.session.add(add_cart_record)
                        db.session.commit()
            else:
                current_slug = slug
                if cart_form.validate_on_submit():
                    add_cart_record = CartRecord(
                        menu_name=cart_form.menu_name.data,
                        slug=slug,
                        price=float(cart_form.price.data))
                    db.session.add(add_cart_record)
                    db.session.commit()


    restaurant = Restaurants.query.filter_by(slug=slug).one()
    menu_items = MenuItems.query.filter_by(slug=slug).order_by(asc(MenuItems.name))
    comments = Feedback.query.filter_by(slug=slug).order_by(asc(Feedback.username))
    return render_template('restaurant.html', restaurant=restaurant, menu_items=menu_items,comments=comments,is_login=is_login,cart_data_len=CartRecord.query.count(),form=form)

@app.route('/login_error')
def login_error():
    return render_template("messages.html",no_button=False, message_title=f"CANNOT ADD TO CART!",
                           message_subtitle="You should login first to use this function", is_error=True)

@app.route('/login_error_2')
def login_error_2():
    return render_template("messages.html",no_button=False, message_title=f"CANNOT COMMENT OR RATE!",
                           message_subtitle="You should login first to use this function", is_error=True)

@app.route('/reservation_success')
def reservation_success():
    return render_template("messages.html",no_button=True, message_title=f"RESERVATION SUCCESS!",
                           message_subtitle="Thank you for visiting our Restaurant:)", is_error=False)

@app.route('/reservation_failed')
def reservation_failed():
    return render_template("messages.html",no_button=True, message_title=f"RESERVATION FAILED!",
                           message_subtitle="Something went wrong!)", is_error=True)


@app.route('/cart/<string:slug>')
def cart(slug):
    cart_data = CartRecord.query.all()
    cart_data_list=[]
    for data in cart_data:
        cart_data_list.append({
            'name' : data.menu_name,
            'amount' : CartRecord.query.filter_by(menu_name=data.menu_name).count(),
            'price' : data.price
        })
    no_dup_cart_data_list = [i for n, i in enumerate(cart_data_list) if i not in cart_data_list[n + 1:]]

    return render_template("cart.html",cart_data_list=no_dup_cart_data_list,slug=slug)


@app.route('/cart')
def empty_cart():
    return render_template("messages.html",no_button=True, message_title=f"CART EMPTY!",
                           message_subtitle=f"Please select a restaurant first and order.", is_error=True)


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
            return render_template("messages.html", no_button=True, message_title=f"ORDER SUCCESS!",
                                   message_subtitle=f"The order has been submitted, wait for it to be delivered Enjoy! :)", is_error=False)
    except Exception as e:
        return render_template("messages.html", no_button=True, message_title=f"ORDER FAILED!",
                               message_subtitle=f"Something went wrong with your request please try again! :)",
                               is_error=False)



if __name__ == "__main__":
    app.run(debug=True,use_debugger=True,use_reloader=True)


