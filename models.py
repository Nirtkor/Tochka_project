from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()  # Database object for interacting with the db

class User(UserMixin, db.Model):
    """
    User table model
    Linked to Roles model and Reservations model
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(300), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'),
                        nullable=False)  # Foreign key for one-to-many with the Roles model
    reservations = db.relationship("Reservation", backref="user", lazy=True,
                                   cascade="all,delete-orphan")  # One-to-many relationship with the Reservations model

class Roles(db.Model):
    """
    Roles table model
    Connected to User model
    """
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    users = db.relationship('User', backref='role', lazy=True,
                            cascade="all, delete-orphan", )  # One-to-many relationship with Users model

class Product(db.Model):
    """
    Coworking Spaces: Product table model
    Connected to the Reservation model
    """
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    area = db.Column(db.Float)
    capacity = db.Column(db.Integer)
    equipment = db.Column(db.Text)

    # Relationship with the Reservation model
    reservations = db.relationship("Reservation", backref="product", lazy=True,
                                   cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Product {self.name}>"

class Reservation(db.Model):
    """
    Reservation table model
    Connected to the Users model and Product model
    """
    __tablename__ = 'reservations'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Text, nullable=False)
    total = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<Reservation {self.id}>"
