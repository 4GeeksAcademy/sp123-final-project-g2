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
        db.select(Users).where(Users.user_id == user_id)
    ).scalar()

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
