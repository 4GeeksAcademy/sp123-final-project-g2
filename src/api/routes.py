"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from flask import Flask, request, Blueprint
from api.models import db, Users, Courses,Modules,Purchases
from api.utils import generate_sitemap, APIException
from flask_cors import CORS


api = Blueprint('api', __name__)
CORS(api)  # Allow CORS requests to this API


@api.route('/users', methods=['GET', 'POST'])
def users():
    response_body = {}

    if request.method == 'GET':
        rows = db.session.execute(db.select(Users)).scalars().all()
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
                    role=data.get('role'),
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


@api.route('/courses', methods=['GET', 'POST'])
def courses():
    response_body = {}

    if request.method == 'GET':
        rows = db.session.execute(db.select(Courses)).scalars().all()
        results = [row.serialize() for row in rows]
        response_body['results'] = results
        response_body['message'] = 'Listado de cursos'
        return response_body, 200

    if request.method == 'POST':
        data = request.json
        row = Courses(title=data.get('title'),
                      description=data.get('description'),
                      price=data.get('price'),
                      is_active=data.get('is_active'),
                      points=data.get('points'),
                      created_by=data.get('created_by'))
        db.session.add(row)
        db.session.commit()

        response_body['results'] = row.serialize()
        response_body['message'] = 'Curso creado'
        return response_body, 201
    return response_body, 404


@api.route('/courses/<int:course_id>', methods=['GET', 'PUT', 'DELETE'])
def course(course_id):
    response_body = {}

    row = db.session.execute(
        db.select(Courses).where(Courses.course_id == course_id)).scalars().all()

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
        row.points = data.get('points', row.points)
        row.created_by = data.get('created_by', row.created_by)

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
        rows = db.session.execute(db.select(Modules)).scalars().all()
        results = [row.serialize() for row in rows]
        response_body['results'] = results
        response_body['message'] = 'Listado de módulos'
        return response_body, 200

    if request.method == 'POST':
        data = request.json
        row = Modules(
            title=data.get('title'),
            order=data.get('order'),
            points=data.get('points'),
            course_id=data.get('course_id')
        )

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
        row.course_id = data.get('course_id', row.course_id)

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


@api.route('/purchases', methods=['GET', 'POST'])
def purchases():
    response_body = {}

    if request.method == 'GET':
        rows = db.session.execute(db.select(Purchases)).scalars().all()
        results = [row.serialize() for row in rows]
        response_body['results'] = results
        response_body['message'] = 'Listado de compras'
        return response_body, 200

    if request.method == 'POST':
        data = request.json
        row = Purchases(
            price=data.get('price'),
            total=data.get('total'),
            status=data.get('status'),
            start_date=data.get('start_date'),
            course_id=data.get('course_id'),
            user_id=data.get('user_id')
        )

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
        db.select(Purchases).where(Purchases.purchase_id == purchase_id)
    ).scalar()

    if not row:
        response_body['message'] = 'Compra no encontrada'
        return response_body, 404

    if request.method == 'GET':
        response_body['results'] = row.serialize()
        response_body['message'] = f'Detalles de la compra {purchase_id}'
        return response_body, 200

    if request.method == 'PUT':
        data = request.json

        row.price = data.get('price', row.price)
        row.total = data.get('total', row.total)
        row.status = data.get('status', row.status)
        row.start_date = data.get('start_date', row.start_date)
        row.course_id = data.get('course_id', row.course_id)
        row.user_id = data.get('user_id', row.user_id)

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
