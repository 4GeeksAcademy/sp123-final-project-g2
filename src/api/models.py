from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from sqlalchemy import UniqueConstraint

db = SQLAlchemy()


class Users(db.Model):
    __tablename__ = "users"
    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.Enum("student", "teacher", "demo", name="role_users"), default="student")
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    current_points = db.Column(db.Integer, default=0, nullable=False)
    is_active = db.Column(db.Boolean(), default=True, nullable=False)
    is_admin = db.Column(db.Boolean(), default=False, nullable=False)
    registration_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    trial_end_date = db.Column(db.DateTime, nullable=True)
    last_access = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<User: {self.user_id} - {self.first_name} {self.last_name}>'

    def serialize(self):
        return {
            "user_id": self.user_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "role": self.role,
            "current_points": self.current_points,
            "is_active": self.is_active,
            "is_admin": self.is_admin,
            "registration_date": self.registration_date.isoformat() if self.registration_date else None,
            "trial_end_date": self.trial_end_date.isoformat() if self.trial_end_date else None,
            "last_access": self.last_access.isoformat() if self.last_access else None
        }


class Courses(db.Model):
    __tablename__ = "courses"
    course_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), unique=True, nullable=False)
    description = db.Column(db.String(600), nullable=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    is_active = db.Column(db.Boolean(), default=True, nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    points = db.Column(db.Integer)
    created_by = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    created_to = db.relationship('Users', foreign_keys=[created_by],
                                 backref=db.backref('users_to_courses', lazy='select'))

    def __repr__(self):
        return f'<Course {self.course_id} - {self.title}>'

    def serialize(self):
        return {
            "course_id": self.course_id,
            "title": self.title,
            "description": self.description,
            "price": float(self.price) if self.price else None,
            "is_active": self.is_active,
            "created_by": self.created_by,
            "creation_date": self.creation_date.isoformat() if self.creation_date else None,
            "points": self.points
        }


class Modules(db.Model):
    __tablename__ = "modules"
    module_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    order = db.Column(db.Integer)
    points = db.Column(db.Integer)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.course_id', ondelete='CASCADE'))
    course_to = db.relationship('Courses', foreign_keys=[course_id],
                                backref=db.backref('modules_to', lazy='select'))

    __table_args__ = (
        UniqueConstraint('course_id', 'order', name='uq_module_order_per_course'),
    )

    def __repr__(self):
        return f'<Modules {self.module_id} - {self.title}>'

    def serialize(self):
        return {
            "module_id": self.module_id,
            "title": self.title,
            "order": self.order,
            "points": self.points,
            "course_id": self.course_id
        }


class Lessons(db.Model):
    __tablename__ = "lessons"
    lesson_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=True)
    content = db.Column(db.Text, nullable=True)
    learning_objective = db.Column(db.Text, nullable=True)
    signs_taught = db.Column(db.String(600), unique=True, nullable=True)
    order = db.Column(db.Integer)
    trial_visible = db.Column(db.Boolean, default=False)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.module_id', ondelete='CASCADE'))
    module_to = db.relationship('Modules', foreign_keys=[module_id],
                                backref=db.backref('lessons_list', lazy='select'))

    __table_args__ = (
        UniqueConstraint('module_id', 'order', name='uq_lesson_order_per_module'),
    )

    def __repr__(self):
        return f'<Lessons {self.lesson_id} - {self.title}>'

    def serialize(self):
        return {
            "lesson_id": self.lesson_id,
            "title": self.title,
            "content": self.content,
            "learning_objective": self.learning_objective,
            "signs_taught": self.signs_taught,
            "order": self.order,
            "trial_visible": self.trial_visible,
            "module_id": self.module_id
        }


class Purchases(db.Model):
    __tablename__ = "purchases"
    purchase_id = db.Column(db.Integer, primary_key=True)
    purchase_date = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    price = db.Column(db.Numeric(10, 2), nullable=False)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.Enum("paid", "pending", "cancelled", name="status"), default="pending")
    start_date = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    course_id = db.Column(db.Integer, db.ForeignKey('courses.course_id', ondelete='RESTRICT'))
    course_to = db.relationship('Courses', foreign_keys=[course_id],
                                backref=db.backref('courses_to', lazy='select'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='RESTRICT'))
    user_to = db.relationship('Users', foreign_keys=[user_id],
                              backref=db.backref('users_to_purchases', lazy='select'))

    __table_args__ = (
        UniqueConstraint('user_id', 'course_id', name='uq_user_course_purchase'),
    )

    def __repr__(self):
        return f'<Purchase {self.purchase_id}>'

    def serialize(self):
        return {
            "purchase_id": self.purchase_id,
            "purchase_date": self.purchase_date.isoformat() if self.purchase_date else None,
            "price": float(self.price) if self.price else None,
            "total": float(self.total) if self.total else None,
            "status": self.status,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "course_id": self.course_id,
            "user_id": self.user_id
        }


class UserPoints(db.Model):
    __tablename__ = "user_points"
    point_id = db.Column(db.Integer, primary_key=True)
    points = db.Column(db.Integer, nullable=False)
    type = db.Column(db.Enum('lesson', 'module', 'course', name='type_user_points'), nullable=False, default="course")
    event_description = db.Column(db.String(255), nullable=True)
    date = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'))
    user_to = db.relationship('Users', foreign_keys=[user_id],
                              backref=db.backref('users_to_points', lazy='select'))

    def __repr__(self):
        return f'<UserPoints {self.point_id} - {self.type}>'

    def serialize(self):
        return {
            "point_id": self.point_id,
            "user_id": self.user_id,
            "points": self.points,
            "type": self.type,
            "event_description": self.event_description,
            "date": self.date.isoformat() if self.date else None
        }


class UserProgress(db.Model):
    __tablename__ = "user_progress"
    progress_id = db.Column(db.Integer, primary_key=True)
    completed = db.Column(db.Boolean(), default=False, nullable=False)
    start_date = db.Column(db.DateTime, nullable=True)
    completion_date = db.Column(db.DateTime, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'))
    user_to = db.relationship('Users', foreign_keys=[user_id],
                              backref=db.backref('user_progress_records', lazy='select'))
    lesson_id = db.Column(db.Integer, db.ForeignKey("lessons.lesson_id", ondelete='CASCADE'), nullable=False)
    lesson_to = db.relationship('Lessons', foreign_keys=[lesson_id],
                                backref=db.backref('lesson_progress', lazy='select'))

    __table_args__ = (
        UniqueConstraint('user_id', 'lesson_id', name='uq_user_lesson_progress'),
    )

    def __repr__(self):
        return f'<UserProgress {self.progress_id} - {self.completed}>'

    def serialize(self):
        return {
            "progress_id": self.progress_id,
            "user_id": self.user_id,
            "lesson_id": self.lesson_id,
            "completed": self.completed,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "completion_date": self.completion_date.isoformat() if self.completion_date else None
        }


class Achievements(db.Model):
    __tablename__ = "achievements"
    achievement_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    required_points = db.Column(db.Integer, nullable=False)
    icon = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f'<Achievements: {self.achievement_id} - {self.name}>'

    def serialize(self):
        return {
            "achievement_id": self.achievement_id,
            "name": self.name,
            "description": self.description,
            "required_points": self.required_points,
            "icon": self.icon
        }


class UserAchievements(db.Model):
    __tablename__ = "user_achievements"
    user_achievement_id = db.Column(db.Integer, primary_key=True)
    obtained_date = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'))
    user_to = db.relationship('Users', foreign_keys=[user_id],
                              backref=db.backref('user_achievements_list', lazy='select'))
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievements.achievement_id', ondelete='CASCADE'))
    achievement_to = db.relationship('Achievements', foreign_keys=[achievement_id],
                                     backref=db.backref('user_achievements_list', lazy='select'))

    __table_args__ = (
        UniqueConstraint('user_id', 'achievement_id', name='uq_user_achievement'),
    )

    def __repr__(self):
        return f'<UserAchievements {self.user_achievement_id}>'

    def serialize(self):
        return {
            "user_achievement_id": self.user_achievement_id,
            "user_id": self.user_id,
            "achievement_id": self.achievement_id,
            "obtained_date": self.obtained_date.isoformat() if self.obtained_date else None
        }


class MultimediaResources(db.Model):
    __tablename__ = "multimedia_resources"
    resource_id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Enum('video', 'image', 'gif', 'animation', 'document', name='type_multimedia_resources'), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    duration_seconds = db.Column(db.Integer, nullable=True)
    description = db.Column(db.String(255), nullable=True)
    order = db.Column(db.Integer, nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.lesson_id', ondelete='CASCADE'))
    lesson_to = db.relationship('Lessons', foreign_keys=[lesson_id],
                                backref=db.backref('multimedia_resources', lazy='select'))

    def __repr__(self):
        return f'<MultimediaResources {self.resource_id} - {self.url} - {self.description}>'

    def serialize(self):
        return {
            "resource_id": self.resource_id,
            "lesson_id": self.lesson_id,
            "type": self.type,
            "url": self.url,
            "duration_seconds": self.duration_seconds,
            "description": self.description,
            "order": self.order
        }
    __tablename__ = "multimedia_resources"
    resource_id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Enum('video', 'image', 'gif', 'animation', 'document', name='type_multimedia_resources'), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    duration_seconds = db.Column(db.Integer, nullable=True)
    description = db.Column(db.String(255), nullable=True)
    order = db.Column(db.Integer, nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.lesson_id', ondelete='CASCADE'))
    lesson_to = db.relationship('Lessons', foreign_keys=[lesson_id],
                                backref=db.backref('multimedia_resources', lazy='select'))

    def __repr__(self):
        return f'<MultimediaResources {self.resource_id} - {self.url} - {self.description}>'

    def serialize(self):
        return {
            "resource_id": self.resource_id,
            "lesson_id": self.lesson_id,
            "type": self.type,
            "url": self.url,
            "duration_seconds": self.duration_seconds,
            "description": self.description,
            "order": self.order
        }