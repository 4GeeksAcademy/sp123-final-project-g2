from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime


db = SQLAlchemy()


class Users(db.Model):
    __tablename__ = "users"
    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), unique=False, nullable=False)
    current_points = db.Column(db.Integer, default=0, nullable=False)
    is_active = db.Column(db.Boolean(), default=True, nullable=False)
    is_admin = db.Column(db.Boolean(), default=False, nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow) 
    trial_end_date = db.Column(db.DateTime, nullable=False)   
    last_access = db.Column(db.DateTime, nullable=True)          

    def __repr__(self):
        return f'<User {self.email}>'

    def serialize(self):
        return {
            "user_id": self.user_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "current_points": self.current_points,
            "is_active": self.is_active,
            "is_admin": self.is_admin,
            "registration_date": self.registration_date,
            "trial_end_date": self.trial_end_date, 
            "last_access": self.last_access}