"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from flask import Flask, request, Blueprint
from api.models import db, Users
from api.utils import generate_sitemap, APIException
from flask_cors import CORS


api = Blueprint('api', __name__)
CORS(api)  # Allow CORS requests to this API


@api.route('/users', methods=['GET', 'POST'])
def users():
    response_body = {}

    if request.method == 'GET':
        rows = db.session.execute(db.select(Users)).scalars.all()
        results = [row.serialize() for row in rows]
        response_body['results'] = results
        response_body['message'] = 'Listado de usuarios'
        return response_body, 200
    if request.method == 'POST':
        data = request.json
        row = Users(email=data.get('email'),
                    password_hash=data.get('password'),
                    first_name=data.get('first_name'),
                    last_name=data.get('last_name'),
                    is_active=True,
                    is_admin=False,
                    current_points=data.get('current_points'),
                    registration_date=data.get('registration_date'),
                    trial_end_date=data.get('trial_end_date'),
                    last_access=data.get('last_acces'))
        db.session.add(row)
        db.session.commit()
        response_body['results'] = row.serialize()
        response_body['message'] = 'Usuario creado'
        return response_body, 201
    return response_body, 404


@api.route('/users/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
def user(user_id):
    response_body = {}

    row = db.session.execute(
        db.select(Users).where(Users.user_id == user_id) ).scalar()

    if not row:
        response_body['message'] = 'Usuario no encontrado'
        return response_body, 404
   if request.method == 'GET':
        response_body['results'] = row.serialize()
        response_body['message'] = f'Detalles del usuario {user_id}'
        return response_body, 200
    if request.method == 'PUT':
        data = request.json

        row.email = data.get('email', row.email)
        row.first_name = data.get('first_name', row.first_name)
        row.last_name = data.get('last_name', row.last_name)
        row.current_points = data.get('current_points', row.current_points)
        row.is_active = data.get('is_active', row.is_active)
        row.is_admin = data.get('is_admin', row.is_admin)
        row.trial_end_date = data.get('trial_end_date', row.trial_end_date)
        row.last_access = data.get('last_access', row.last_access)

        db.session.commit()

        response_body['results'] = row.serialize()
        response_body['message'] = f'Usuario {user_id} actualizado'
        return response_body, 200

    if request.method == 'DELETE':
        db.session.delete(row)
        db.session.commit()

        response_body['message'] = f'Usuario {user_id} eliminado'
        return response_body, 200

@api.route('/user-points', methods=['GET', 'POST'])
def user_points():
    response_body = {}

    if request.method == 'GET':
        rows = db.session.execute(
            db.select(UserPoints) ).scalars().all()
        results = [row.serialize() for row in rows]
        response_body['results'] = results
        response_body['message'] = 'Listado de puntos de usuarios'
        return response_body, 200

    if request.method == 'POST':
        data = request.json

        row = UserPoints(
            user_id=data.get('user_id'),
            points=data.get('points'),
            type=data.get('type', 'course'),
            event_description=data.get('event_description'),
            date=data.get('date') )

        db.session.add(row)
        db.session.commit()

        response_body['results'] = row.serialize()
        response_body['message'] = 'Puntos de usuario creados'
        return response_body, 201

    return response_body, 404

@api.route('/user-points/<int:point_id>', methods=['GET', 'PUT', 'DELETE'])
def user_point(point_id):
    response_body = {}

    row = db.session.execute(
        db.select(UserPoints).where(UserPoints.point_id == point_id)).scalar()

    if not row:
        response_body['message'] = 'Registro de puntos no encontrado'
        return response_body, 404

    if request.method == 'GET':
        response_body['results'] = row.serialize()
        response_body['message'] = f'Detalles del punto {point_id}'
        return response_body, 200

    if request.method == 'PUT':
        data = request.json

        row.points = data.get('points', row.points)
        row.type = data.get('type', row.type)
        row.event_description = data.get('event_description', row.event_description)
        row.date = data.get('date', row.date)
        row.user_id = data.get('user_id', row.user_id)

        db.session.commit()

        response_body['results'] = row.serialize()
        response_body['message'] = f'Punto {point_id} actualizado'
        return response_body, 200

    if request.method == 'DELETE':
        db.session.delete(row)
        db.session.commit()

        response_body['message'] = f'Punto {point_id} eliminado'
        return response_body, 200

@api.route('/achievements', methods=['GET', 'POST'])
def achievements():
    response_body = {}

    if request.method == 'GET':
        rows = db.session.execute(
            db.select(Achievements) ).scalars().all()
        results = [row.serialize() for row in rows]
        response_body['results'] = results
        response_body['message'] = 'Listado de logros'
        return response_body, 200

    if request.method == 'POST':
        data = request.json

        row = Achievements(
            name=data.get('name'),
            description=data.get('description'),
            required_points=data.get('required_points'),
            icon=data.get('icon')
        )

        db.session.add(row)
        db.session.commit()

        response_body['results'] = row.serialize()
        response_body['message'] = 'Logro creado'
        return response_body, 201

    return response_body, 404

@api.route('/achievements/<int:achievement_id>', methods=['GET', 'PUT', 'DELETE'])
def achievement(achievement_id):
    response_body = {}

    row = db.session.execute(
        db.select(Achievements).where(Achievements.achievement_id == achievement_id) ).scalar()
    if not row:
        response_body['message'] = 'Logro no encontrado'
        return response_body, 404
    if request.method == 'GET':
        response_body['results'] = row.serialize()
        response_body['message'] = f'Detalles del logro {achievement_id}'
        return response_body, 200

    if request.method == 'PUT':
        data = request.json

        row.name = data.get('name', row.name)
        row.description = data.get('description', row.description)
        row.required_points = data.get('required_points', row.required_points)
        row.icon = data.get('icon', row.icon)

        db.session.commit()

        response_body['results'] = row.serialize()
        response_body['message'] = f'Logro {achievement_id} actualizado'
        return response_body, 200

    if request.method == 'DELETE':
        db.session.delete(row)
        db.session.commit()

        response_body['message'] = f'Logro {achievement_id} eliminado'
        return response_body, 200

@api.route('/user-achievements', methods=['GET', 'POST'])
def user_achievements():
    response_body = {}

    if request.method == 'GET':
        rows = db.session.execute(
            db.select(UserAchievements) ).scalars().all()
        results = [row.serialize() for row in rows]
        response_body['results'] = results
        response_body['message'] = 'Listado de logros obtenidos por usuarios'
        return response_body, 200

    if request.method == 'POST':
        data = request.json
        row = UserAchievements(
            user_id=data.get('user_id'),
            achievement_id=data.get('achievement_id'),
            obtained_date=data.get('obtained_date') )

        db.session.add(row)
        db.session.commit()

        response_body['results'] = row.serialize()
        response_body['message'] = 'Logro asignado al usuario'
        return response_body, 201

    return response_body, 404

@api.route('/user-achievements/<int:user_achievement_id>', methods=['GET', 'PUT', 'DELETE'])
def user_achievement(user_achievement_id):
    response_body = {}

    row = db.session.execute(
        db.select(UserAchievements).where(
            UserAchievements.user_achievement_id == user_achievement_id ) ).scalar()

    if not row:
        response_body['message'] = 'Logro de usuario no encontrado'
        return response_body, 404
    if request.method == 'GET':
        response_body['results'] = row.serialize()
        response_body['message'] = f'Detalles del logro de usuario {user_achievement_id}'
        return response_body, 200
    if request.method == 'PUT':
        data = request.json

        row.user_id = data.get('user_id', row.user_id)
        row.achievement_id = data.get('achievement_id', row.achievement_id)
        row.obtained_date = data.get('obtained_date', row.obtained_date)

        db.session.commit()

        response_body['results'] = row.serialize()
        response_body['message'] = f'Logro de usuario {user_achievement_id} actualizado'
        return response_body, 200

    if request.method == 'DELETE':
        db.session.delete(row)
        db.session.commit()

        response_body['message'] = f'Logro de usuario {user_achievement_id} eliminado'
        return response_body, 200
