from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum, Numeric, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime


db = SQLAlchemy()

"""
 ============================================
 MODULE 2: COURSES AND EDUCATIONAL CONTENT
 ============================================
"""

class Courses(db.Model):
      course_id = db.Column(db.Integer, primary_key=True)
      title = db.Column(db.String(150), unique=True, nullable=True)
      description = db.Column(db.String(600), unique=True, nullable=True)
      price = db.Column(Numeric(10, 2), nullable=False)
      is_active = db.Column(db.Boolean(), unique=False, nullable=False)
      created_by = db.Column(db.Integer, nullable=False)
      creation_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
      points = db.Column(db.Integer)

      # Relacion con Users
      user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
      user_to = db.relationship('Users', foreign_keys=[user_id],
                              backref=db.backref('purchases_to', lazy='select'))

      def __repr__(self):
        return f'<Course {self.course_id}>'
      
      def serialize(self):
          return{"course_id": self.course_id, 
                 "title": self.title,
                 "description": self.description,
                 "price": self.price,
                 "is_active": self.is_active,
                 "created_by": self.created_by,
                 "creation_date": self.creation_date,
                 "points": self.points,
                 "user_id": self.user_id}
      
class Modules(db.Model):
  module_id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(150), unique=True, nullable=False)
  order = db.Column(db.Integer)
  points = db.Column(db.Integer)

  # Relacion con Courses
  course_id = db.Column(db.Integer, db.ForeignKey('courses.course_id'))
  course_to = db.relationship('Courses', foreign_keys=[course_id],
                              backref=db.backref('modules_to', lazy='select'))
  
  def __repr__(self):
      return f'<Modules {self.module_id}>'
  
  def serialize(self):
      return{"module_id": self.module_id,
             "title": self.title,
             "order": self.order,
             "points": self.points,
             "course_id": self.course_id,}

class Lessons(db.Model):
  lesson_id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(150), unique=True, nullable=True)
  content = db.Column(db.String(600), unique=True, nullable=True)
  learning_objective = db.Column(db.String(600), unique=True, nullable=True)
  signs_taught = db.Column(db.String(600), unique=True, nullable=True)
  order = db.Column(db.Integer)
  trial_visible = db.Column(db.Boolean, default=False)

  # Relacion con Modules
  module_id = db.Column(db.Integer, db.ForeignKey('modules.module_id'))
  module_to = db.relationship('Modules', foreign_keys=[module_id],
                              backref=db.backref('lessons_to', lazy='select'))
  
  def __repr__(self):
      return f'<Lessons {self.lesson_id}>'
  
  def serialize(self):
      return{"lesson_id": self.lesson_id,
             "title": self.title,
             "content": self.content,
             "learning_objective": self.learning_objective,
             "signs_taught": self.signs_taught,
             "order": self.order,
             "trial_visible": self.trial_visible,
             "module_id": self.module_id}

"""
 ============================================
 MODULE 3: ACCESS AND SUBSCRIPTIONS
 ============================================
"""

class Purchases(db.Model): 
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
                                backref=db.backref('purchase_to', lazy='select'))
    
    # Relacion con Users
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    user_to = db.relationship('Users', foreign_keys=[user_id],
                              backref=db.backref('purchases_to', lazy='select'))

    def __repr__(self):
        return f'<Purchase {self.purchase_id}>'
    
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
