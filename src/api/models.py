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
        return f'<UserAchievements {self.user_achievement_id}>'

   
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
        


class UserPoints(db.Model):
    point_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    points = db.Column(db.Integer, unique=False, nullable=False)
    type = db.Column(db.Enum('lesson', 'module', 'course', name='points_type'), unique=False, nullable=False)
    event_description = db.Column(db.String(255), unique=False, nullable=True)
    date = db.Column(db.DateTime, unique=False, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<UserPoints {self.point_id}>'

    def serialize(self):
        return {"point_id": self.point_id,
                "user_id": self.user_id,
                "points": self.points,
                "type": self.type,
                "event_description": self.event_description,
                "date": self.date}


class UserProgress(db.Model):
    progress_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey("lessons.lesson_id"), nullable=False)
    completed = db.Column(db.Boolean(), unique=False, nullable=False)
    start_date = db.Column(db.DateTime, unique=False, nullable=True)
    completion_date = db.Column(db.DateTime, unique=False, nullable=True)

    def __repr__(self):
        return f'<UserProgress {self.progress_id}>'

    def serialize(self):
        return {"progress_id": self.progress_id,
                "user_id": self.user_id,
                "lesson_id": self.lesson_id,
                "completed": self.completed,
                "start_date": self.start_date,
                "completion_date": self.completion_date}


class Achievements(db.Model):
    achievement_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=False, nullable=False)
    description = db.Column(db.String(255), unique=False, nullable=False)
    required_points = db.Column(db.Integer, unique=False, nullable=False)
    icon = db.Column(db.String(100), unique=False, nullable=True)

    def __repr__(self):
        return f'<Achievements {self.name}>'

    def serialize(self):
        return {"achievement_id": self.achievement_id,
                "name": self.name,
                "description": self.description,
                "required_points": self.required_points,
                "icon": self.icon}


class UserAchievements(db.Model):
    user_achievement_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey("achievements.achievement_id"), nullable=False)
    obtained_date = db.Column(db.DateTime, unique=False, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return {"user_achievement_id": self.user_achievement_id,
                "user_id": self.user_id,
                "achievement_id": self.achievement_id,
                "obtained_date": self.obtained_date}  
    

class MultimediaResources(db.Model):
    resource_id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey("lessons.lesson_id"), nullable=False)
    type = db.Column(db.Enum('video', 'image', 'gif', 'animation', 'document', name='multimedia_type'), unique=False, nullable=False)
    url = db.Column(db.String(500), unique=False, nullable=False)
    duration_seconds = db.Column(db.Integer, unique=False, nullable=True)
    description = db.Column(db.String(255), unique=False, nullable=True)
    order = db.Column(db.Integer, unique=False, nullable=False)

    def __repr__(self):
        return f'<MultimediaResources {self.resource_id}>'

    def serialize(self):
        return {"resource_id": self.resource_id,
                "lesson_id": self.lesson_id,
                "type": self.type,
                "url": self.url,
                "duration_seconds": self.duration_seconds,
                "description": self.description,
                "order": self.order}
        