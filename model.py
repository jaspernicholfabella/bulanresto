
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, BLOB,desc,asc, Boolean
from config import setup_app

db = SQLAlchemy(setup_app())


## Database Class
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String,unique=True)
    password = Column(String)
    name = Column(String)
    emailaddress = Column(String)
    homeaddress  = Column(String)
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
    userid = Column(Integer)
    slug = Column(String)
    cartitems=Column(String)
    address = Column(String)
    date = Column(DateTime)
    total = Column(Float)
    delivered = Column(Boolean,default=False)

class Feedback(db.Model):
    __tablename__ = 'feedback'
    id = Column(Integer,primary_key=True)
    username = Column(String)
    slug = Column(String)
    rate = Column(Float)
    comment = Column(String)

class CartRecord(db.Model):
    __tablename__ = 'cartrecord'
    id = Column(Integer,primary_key=True)
    menu_name = Column(String)
    slug=Column(String)
    price=Column(Float)

class ReservationSetup(db.Model):
    __tablename__ = 'reservation_setup'
    id = Column(Integer,primary_key=True)
    month = String(unique=True)
    skip_dates = String()
    business_hours_start=(String())
    business_hours_end=(String())
    table_slots = Integer()

class Reservations(db.Model):
    __tablename__ = 'reservations'


