"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from flask import Flask, request, Blueprint
from api.models import db, Users, Courses,Modules,Purchases, MultimediaResources, Lessons
from api.utils import generate_sitemap, APIException
from flask_cors import CORS


api = Blueprint('api', __name__)
CORS(api)  # Allow CORS requests to this API


@api.route('/users', methods=['GET', 'POST'])
def users():
    response_body = {}

    if request.method == 'GET':
        rows = db.session.execute(db.select(Users)).scalars()
        results = [row.serialize() for row in rows]
        response_body['results'] = results
        response_body['message'] = 'Listado de usuarios'
        return response_body, 200
    if request.method == 'POST':
        data = request.json
        row = Users(first_name=data.get('first_name'),
                    last_name=data.get('last_name'),
                    role=data.get('role'),
                    email=data.get('email'),
                    password_hash=data.get('password'),
                    current_points=data.get('current_points'),
                    is_active=True,
                    is_admin=False,
                    registration_date=data.get('registration_date'),
                    trial_end_date=data.get('trial_end_date'),
                    last_access=data.get('last_access'))
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
        db.select(Users).where(Users.user_id == user_id)).scalar()

    if not row:
        response_body['message'] = 'Usuario no encontrado'
        return response_body, 404

    if request.method == 'GET':
        response_body['results'] = row.serialize()
        response_body['message'] = f'Detalles del usuario {user_id}'
        return response_body, 200

    if request.method == 'PUT':
        data = request.json
        row.first_name = data.get('first_name', row.first_name)
        row.last_name = data.get('last_name', row.last_name)
        row.role = data.get('role', row.role)
        row.email = data.get('email', row.email)
        ##row.password_hash = data.get('password', row.password_hash)
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

@api.route('/courses', methods=['GET', 'POST'])
def courses():
    response_body = {}

    if request.method == 'GET':
        rows = db.session.execute(db.select(Courses)).scalars()
        results = [row.serialize() for row in rows]
        response_body['results'] = results
        response_body['message'] = 'Listado de cursos'
        return response_body, 200
    if request.method == 'POST':
        data = request.json
        #Verificar que las claves lleguen (todas las que se requieran y no estan todas le devuenlvo al usuario un 400)
        row = MultimediaResources(title=data.get('title', None),
                                  description=data.get('description'),
                                  price=data.get('price'),
                                  is_active=data.get('is_active'),
                                  creation_date=data.get('creation_date'),
                                  points=data.get('points'))                                 
        db.session.add(row)
        db.session.commit()
        response_body['results'] = row.serialize()
        response_body['message'] = 'Multimedia creado'
        return response_body, 201
    return response_body, 404

@api.route('/courses/<int:course_id>', methods=['GET', 'PUT', 'DELETE'])
def course(course_id):
    response_body = {}

    row = db.session.execute(
        db.select(Courses).where(Courses.course_id == course_id)).scalar()

    if not row:
        response_body['message'] = 'Curso no encontrado'
        return response_body, 404
    if request.method == 'GET':
        response_body['results'] = row.serialize()
        response_body['message'] = f'Detalles del curso {course_id}'
        return response_body, 200
    if request.method == 'PUT':
        data = request.json
        row.title = data.get('title', row.title)
        row.description = data.get('description', row.description)
        row.price = data.get('price', row.price)
        row.is_active = data.get('is_active', row.is_active)
        row.creation_date = data.get('creation_date', row.creation_date)
        row.points = data.get('points', row.points)
        db.session.commit()
        response_body['results'] = row.serialize()
        response_body['message'] = f'Curso {course_id} actualizado'
        return response_body, 200
    if request.method == 'DELETE':
        db.session.delete(row)
        db.session.commit()
        response_body['message'] = f'Curso {course_id} eliminado'
        return response_body, 200
    return response_body, 404

@api.route('/modules', methods=['GET', 'POST'])
def modules():
    response_body = {}

    if request.method == 'GET':
        rows = db.session.execute(db.select(Modules)).scalars()
        results = [row.serialize() for row in rows]
        response_body['results'] = results
        response_body['message'] = 'Listado de módulos'
        return response_body, 200
    if request.method == 'POST':
        data = request.json
        row = Modules(title=data.get('title'),
                      order=data.get('order'),
                      points=data.get('points'))
        db.session.add(row)
        db.session.commit()
        response_body['results'] = row.serialize()
        response_body['message'] = 'Módulo creado'
        return response_body, 201
    return response_body, 404

@api.route('/modules/<int:module_id>', methods=['GET', 'PUT', 'DELETE'])
def module(module_id):
    response_body = {}

    row = db.session.execute(
        db.select(Modules).where(Modules.module_id == module_id)).scalar()

    if not row:
        response_body['message'] = 'Módulo no encontrado'
        return response_body, 404
    if request.method == 'GET':
        response_body['results'] = row.serialize()
        response_body['message'] = f'Detalles del módulo {module_id}'
        return response_body, 200
    if request.method == 'PUT':
        data = request.json
        row.title = data.get('title', row.title)
        row.order = data.get('order', row.order)
        row.points = data.get('points', row.points)
        db.session.commit()
        response_body['results'] = row.serialize()
        response_body['message'] = f'Módulo {module_id} actualizado'
        return response_body, 200
    if request.method == 'DELETE':
        db.session.delete(row)
        db.session.commit()
        response_body['message'] = f'Módulo {module_id} eliminado'
        return response_body, 200
    return response_body, 404

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
                      learning_objective=data.get('learning_objective'),
                      signs_taught=data.get('signs_taught'),
                      order=data.get('order'),
                      trial_version=data.get('trial_version'))
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
        row.learning_objective = data.get('learning_objective', row.learning_objective)
        row.signs_taught = data.get('signs_taught', row.signs_taught)
        row.order = data.get('order', row.order)
        row.trial_version = data.get('trial_version', row.trial_version)
        db.session.commit()
        response_body['results'] = row.serialize()
        response_body['message'] = f'Lección {lesson_id} actualizada'
        return response_body, 200
    if request.method == 'DELETE':
        db.session.delete(row)
        db.session.commit()
        response_body['message'] = f'Lección {lesson_id} eliminada'
        return response_body, 200

@api.route('/purchases', methods=['GET', 'POST'])
def purchases():
    response_body = {}

    if request.method == 'GET':
        rows = db.session.execute(db.select(Purchases)).scalars()
        results = [row.serialize() for row in rows]
        response_body['results'] = results
        response_body['message'] = 'Listado de compras'
        return response_body, 200

    if request.method == 'POST':
        data = request.json
        row = Purchases(purchase_date=data.get('purchase_date'),
                        price=data.get('price'),
                        total=data.get('total'),
                        status=data.get('status'),
                        start_date=data.get('start_date'))
        db.session.add(row)
        db.session.commit()

        response_body['results'] = row.serialize()
        response_body['message'] = 'Compra creada'
        return response_body, 201
    return response_body, 404

@api.route('/purchases/<int:purchase_id>', methods=['GET', 'PUT', 'DELETE'])
def purchase(purchase_id):
    response_body = {}

    row = db.session.execute(
        db.select(Purchases).where(Purchases.purchase_id == purchase_id)).scalar()

    if not row:
        response_body['message'] = 'Compra no encontrada'
        return response_body, 404
    if request.method == 'GET':
        response_body['results'] = row.serialize()
        response_body['message'] = f'Detalles de la compra {purchase_id}'
        return response_body, 200
    if request.method == 'PUT':
        data = request.json
        row.purchase_date = data.get('purchase_date', row.purchase_date)
        row.price = data.get('price', row.price)
        row.total = data.get('total', row.total)
        row.status = data.get('status', row.status)
        row.start_date = data.get('start_date', row.start_date)
        db.session.commit()
        response_body['results'] = row.serialize()
        response_body['message'] = f'Compra {purchase_id} actualizada'
        return response_body, 200
    if request.method == 'DELETE':
        db.session.delete(row)
        db.session.commit()
        response_body['message'] = f'Compra {purchase_id} eliminada'
        return response_body, 200
    return response_body, 404

#UserPoints

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
        rows = Lessons(completed=data.get('completed'),
                       start_date=data.get('start_date'),
                       completion_date=data.get('completion_date'))
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
        row.completed = data.get('completed', row.completed)
        row.start_date = data.get('start_date', row.start_date)
        row.completion_date = data.get('completion_date', row.completion_date)
        db.session.commit()
        response_body['results'] = row.serialize()
        response_body['message'] = f'Progreso de usuario {lesson_id} actualizado'
        return response_body, 200
    if request.method == 'DELETE':
        db.session.delete(row)
        db.session.commit()
        response_body['message'] = f'Progreso de usuario {lesson_id} eliminado'
        return response_body, 200

#Archivements

#UserArchivements

@api.route('/multimedia-resources', methods=['GET', 'POST'])
def multimedia_resources():
    response_body = {}

    if request.method == 'GET':
        rows = db.session.execute(db.select(MultimediaResources)).scalars()
        results = [row.serialize() for row in rows]
        response_body['results'] = results
        response_body['message'] = 'Listado de recursos multimedia'
        return response_body, 200

    if request.method == 'POST':
        data = request.json
        row = MultimediaResources(type=data.get('type'),
                                  url=data.get('url'),
                                  duration_seconds=data.get('duration_seconds'),
                                  description=data.get('description'),
                                  order=data.get('order'))
        db.session.add(row)
        db.session.commit()
        response_body['results'] = row.serialize()
        response_body['message'] = 'Recurso multimedia creado'
        return response_body, 201

    return response_body, 404

@api.route('/multimedia-resources/<int:resource_id>', methods=['GET', 'PUT', 'DELETE'])
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
        row.type = data.get('type', row.type)
        row.url = data.get('url', row.url)
        row.duration_seconds = data.get('duration_seconds', row.duration_seconds)
        row.description = data.get('description', row.description)
        row.order = data.get('order', row.order)
        db.session.commit()
        response_body['results'] = row.serialize()
        response_body['message'] = f'Recurso multimedia {resource_id} actualizado'
        return response_body, 200
    if request.method == 'DELETE':
        db.session.delete(row)
        db.session.commit()
        response_body['message'] = f'Recurso multimedia {resource_id} eliminado'
        return response_body, 200
