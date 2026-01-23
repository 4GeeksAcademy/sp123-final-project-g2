"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from flask import Flask, request, Blueprint
from api.models import db, Users, MultimediaResources, Lessons
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
    



@api.route('/multimediaResources', methods=['GET', 'POST'])
def MultimediaResources():
    response_body = {}

    if request.method == 'GET':
        rows = db.session.execute(db.select(MultimediaResources)).scalars
        results = [row.serialize() for row in rows]
        response_body['results'] = results
        response_body['message'] = 'Listado multimedia'
        return response_body, 200

    if request.method == 'POST':
        data = request.json
        #Verificar que las claves lleguen (todas las que se requieran y no estan todas le devuenlvo al usuario un 400)
        row = MultimediaResources(title=data.get('title', None),
                                  description=data.get('description'),
                                  file_url=data.get('file_url'),
                                  file_type=data.get('file_type'),
                                  duration=data.get('duration'),
                                  is_active=data.get('is_active'))
        db.session.add(row)
        db.session.commit()
        response_body['results'] = row.serialize()
        response_body['message'] = 'Multimedia creado'
        return response_body, 201

    return response_body, 404

@api.route('/multimediaResources/<int:resource_id>', methods=['GET', 'PUT', 'DELETE'])
def multimedia_resource(resource_id):
    response_body = {}

    row = db.session.execute(db.select(MultimediaResources).where
    (MultimediaResources.resource_id == resource_id)).scalar()

    if not row:
        response_body['message'] = 'Recurso multimedia no encontrado'
        return response_body, 404
    if request.method == 'GET':
        response_body['results'] = row.serialize()
        response_body['message'] = f'Detalles del recurso multimedia {resource_id}'
        return response_body, 200
    if request.method == 'PUT':
        data = request.json
        #Verificar que las claves lleguen (todas las que se requieran y no estan todas le devuenlvo al usuario un 400)
        row.title = data.get('title', row.title)
        row.description = data.get('description', row.description)
        row.file_url = data.get('file_url', row.file_url)
        row.file_type = data.get('file_type', row.file_type)
        row.duration = data.get('duration', row.duration)
        row.is_active = data.get('is_active', row.is_active)
        db.session.commit()
        response_body['results'] = row.serialize()
        response_body['message'] = f'Recurso multimedia {resource_id} actualizado'
        return response_body, 200
    if request.method == 'DELETE':
        db.session.delete(row)
        db.session.commit()
        response_body['message'] = f'Recurso multimedia {resource_id} eliminado'
        return response_body, 200

@api.route('/lessons', methods=['GET', 'POST'])
def lessons():
    response_body = {}
    
    if request.method == 'GET':
        rows = db.session.execute(db.select(Lessons)).scalars()
        results = [row.serialize() for row in rows]
        response_body['results'] = results
        response_body['message'] = 'Listado de lecciones'
        return response_body, 200
    
    if request.method == 'POST':
        data = request.json
        row = Lessons(title=data.get('title'),
                      content=data.get('content'),
                      multimedia_resource_id=data.get('multimedia_resource_id'),
                      created_at=data.get('created_at'),
                      updated_at=data.get('updated_at'))
        db.session.add(row)
        db.session.commit()
        response_body['results'] = row.serialize()
        response_body['message'] = 'Lección creada'
        return response_body, 201

@api.route('/lessons/<int:lesson_id>', methods=['GET', 'PUT', 'DELETE'])
def lesson(lesson_id):
    response_body = {}
    
    row = db.session.execute(
        db.select(Lessons).where
        (Lessons.lesson_id == lesson_id)).scalar()

    if not row:
        response_body['message'] = 'Lección no encontrada'
        return response_body, 404
    if request.method == 'GET':
        response_body['results'] = row.serialize()
        response_body['message'] = f'Detalles de la lección {lesson_id}'
        return response_body, 200
    if request.method == 'PUT':
        data = request.json   
        row.title = data.get('title', row.title)
        row.content = data.get('content', row.content)
        row.multimedia_resource_id = data.get('multimedia_resource_id', row.multimedia_resource_id)
        db.session.commit()
        response_body['results'] = row.serialize()
        response_body['message'] = f'Lección {lesson_id} actualizada'
        return response_body, 200
    if request.method == 'DELETE':
        db.session.delete(row)
        db.session.commit()
        response_body['message'] = f'Lección {lesson_id} eliminada'
        return response_body, 200

@api.route('/userprogress', methods=['GET', 'POST'])
def user_progress():
    response_body = {}

    if request.method == 'GET':
        rows = db.session.execute(db.select(Users)).scalars()
        results = [row.serialize() for row in rows]
        response_body['results'] = results
        response_body['message'] = 'Listado de progreso de usuarios'
        return response_body, 200
    
    if request.method == 'POST':
        data = request.json
        rows = Lessons(title=data.get('title'),
                       content=data.get('content'),
                       multimedia_resource_id=data.get('multimedia_resource_id'),
                       created_at=data.get('created_at'),
                       updated_at=data.get('updated_at'))
        db.session.add(rows)
        db.session.commit()
        response_body['results'] = rows.serialize()
        response_body['message'] = 'Progreso de usuario creado'
        return response_body, 201
    
@api.route('/userprogress/<int:lesson_id>', methods=['GET', 'PUT', 'DELETE'])
def user_progress_detail(lesson_id):
    response_body = {}
    row = db.session.execute(db.select(Lessons).where
        (Lessons.lesson_id == lesson_id)).scalar()

    if not row:
        response_body['message'] = 'Progreso de usuario no encontrado'
        return response_body, 404
    if request.method == 'GET':
        response_body['results'] = row.serialize()
        response_body['message'] = f'Detalles del progreso de usuario {lesson_id}'
        return response_body, 200
    if request.method == 'PUT':
        data = request.json  
        row.title = data.get('title', row.title)
        row.content = data.get('content', row.content)
        row.multimedia_resource_id = data.get('multimedia_resource_id', row.multimedia_resource_id)
        db.session.commit()
        response_body['results'] = row.serialize()
        response_body['message'] = f'Progreso de usuario {lesson_id} actualizado'
        return response_body, 200
    if request.method == 'DELETE':
        db.session.delete(row)
        db.session.commit()
        response_body['message'] = f'Progreso de usuario {lesson_id} eliminado'
        return response_body, 200