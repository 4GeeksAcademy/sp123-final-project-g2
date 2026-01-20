from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum, Numeric, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime


db = SQLAlchemy()


## ============================================
## MODULE 3: ACCESS AND SUBSCRIPTIONS
## ============================================

class purchases(db.Model): 
    purchase_id = db.Column(db.Integer, primary_key=True)
    purchase_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    price = db.Column(Numeric(10, 2))
    total = db.Column(Numeric(10, 2))
    status = db.Column(Enum("paid",
                            "pending",
                            "cancelled", name="purchase_status_enum"), default="pending")
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


    # Relacion con Courses
    course_id = db.Column(db.Integer, db.ForeignKey('courses.course_id'))
    course_to = db.relationship('Courses', foreign_keys=[course_id],
                                backref=db.backref('post_to', lazy='select'))
    
    # Relacion con Users
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    user_to = db.relationship('Users', foreign_keys=[user_id],
                              backref=db.backref('post_to', lazy='select'))
    
    def serialize(self):
        return{"purchase_id": self.purchase_id,
               "purchase_date": self.purchase_date,
               "price": self.price,
               "total": self.total,
               "status": self.status,
               "start_date": self.start_date,
               "course_id": self.course_id,
               "user_id": self.user_id}
    


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)

    def __repr__(self):
        return f'<User {self.email}>'

    def serialize(self):
        return {"id": self.id, 
                "email": self.email,
                'is_active': self.is_active}
