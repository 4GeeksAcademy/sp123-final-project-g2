from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from datetime import datetime


db = SQLAlchemy()

    
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