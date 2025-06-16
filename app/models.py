from flask_login import UserMixin
from .extensions import db 
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    password = db.Column(db.String(100), nullable=False)

    cart_items = db.relationship('CartItem', back_populates='user', cascade='all, delete-orphan', passive_deletes=True)
    reviews = db.relationship('Review', backref='user', cascade='all, delete-orphan', passive_deletes=True)
    orders = db.relationship('Order', back_populates='user', cascade='all, delete-orphan', passive_deletes=True)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    user = db.relationship('User', back_populates='orders')
    date = db.Column(db.DateTime)
    total_price = db.Column(db.Float)
    status = db.Column(db.String(50))
    name = db.Column(db.String(100))
    phone = db.Column(db.String(20)) 
    delivery_method = db.Column(db.String(20))
    address = db.Column(db.String(255)) 
    pickup_location = db.Column(db.String(255)) 
    items = db.relationship('OrderItem', backref='order', cascade='all, delete-orphan', passive_deletes=True)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id', ondelete="CASCADE"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    book = db.relationship('Book', lazy=True)
    price_per_item = db.Column(db.Float, nullable=False)
    book_title = db.Column(db.String(256), nullable=False)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    author = db.Column(db.String(120))
    year = db.Column(db.Integer)
    price = db.Column(db.Float)
    genre = db.Column(db.String(100))
    category = db.Column(db.String(100))
    cover = db.Column(db.String(255))
    description = db.Column(db.Text)
    rating = db.Column(db.Float)

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    user = db.relationship('User', back_populates='cart_items')
    book = db.relationship('Book')

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    book = db.relationship('Book')

