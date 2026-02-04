"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from datetime import date
from flask import Flask, request, Blueprint
from api.models import db, Users, Courses, Modules, Purchases, MultimediaResources, Lessons, Achievements, UserPoints, UserAchievements
from api.utils import generate_sitemap, APIException
from flask_cors import CORS
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt



CURRENT_USER_ID = 1

api = Blueprint('api', __name__)
CORS(api)  # Allow CORS requests to this API


@api.route("/login", methods=["POST"])
def login():
    response_body = {}
    email = request.json.get("email", None)
    password_hash = request.json.get("password", None)
    # Validar con mi BD
    row = db.session.execute(db.select(Users).where(Users.email == email,
                                           Users.password_hash == password_hash,
                                           Users.is_active)).scalar()
    if not row:
        response_body['message'] = "Bad username or password"
        return response_body, 401
    
    user = row.serialize()
    user = {'user_id': user['user_id'],
              'is_active': user['is_active'],
              'role': user['role'],
              'is_admin': user['is_admin']}
    response_body['message'] = 'User logged, ok'
    response_body['results'] = user 
    response_body['access_token'] = create_access_token(identity=email, additional_claims=user)
    return response_body, 200


@api.route("/protected", methods=["GET"])
@jwt_required()  
def protected():
    response_body = {} 
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()  #devuelve elidentity email
    additional_user= get_jwt()  #Los datos adiconales
    
    print(current_user)
    print(additional_user['user_id'])
    response_body['message'] = "Autorizado para ver esta información"
    response_body['results'] = current_user
    return response_body, 200


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
        row = Users(email=data.get('email'),
                    password_hash=data.get('password'),
                    first_name=data.get('first_name'),
                    last_name=data.get('last_name'),
                    role='demo',
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
    return response_body, 404

@api.route('/courses-public', methods=['GET'])
def courses_public():
    response_body = {}

    if request.method == 'GET':
        rows = db.session.execute(db.select(Courses)).scalars()
        results = [row.serialize() for row in rows]
        response_body['results'] = results
        response_body['message'] = 'Listado de cursos'
        return response_body, 200
    return response_body, 405

@api.route('/courses-private', methods=['GET', 'POST'])
@jwt_required()
def courses_private():
    response_body = {}

    # validacion de rol de usuario
    user = get_jwt()
    print(user)
    if not user.get('is_active'):
        response_body['message'] = 'Usuario no autorizado'
        return response_body, 403

    if request.method == 'GET':
        rows = db.session.execute(db.select(Courses)).scalars()
        results = [row.serialize() for row in rows]
        response_body['results'] = results
        response_body['message'] = 'Listado de cursos'
        return response_body, 200
    
    if request.method == 'POST':
        # Solo admin y profesor pueden crear cursos
        if not user['is_admin']:
            if user['role'] != 'teacher':
                response_body['message'] = 'No autorizado para crear cursos, no es admin ni teacher'
                return response_body, 403
        # Se valida que el request body no esté vacío
        data = request.json
        if not data:
            response_body['message'] = 'Request body requerido'
            return response_body, 400
        # se valida que las claves requeridas estén en el request body
        required_fields = ['title', 'price', 'points']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            response_body['message'] = 'Faltan campos requeridos'
            response_body['missing_fields'] = missing_fields
            return response_body, 400
        row = Courses(title=data.get('title', None),
                      description=data.get('description', 'info no disponible'),
                      price=data.get('price'),
                      is_active=data.get('is_active', True),
                      points=data.get('points'),
                      created_by=user.get('email'))
        db.session.add(row)
        db.session.commit()

        response_body['results'] = row.serialize()
        response_body['message'] = 'Curso creado'
        return response_body, 201   
    return response_body, 405

@api.route('/courses-private/<int:course_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def course_private(course_id):
    response_body = {}
    # validacion de rol de usuario
    user = get_jwt()
    print(user)
    if not user.get('is_active'):
        response_body['message'] = 'Usuario no autorizado'
        return response_body, 403
    
    #Se busca el curso por ID
    row = db.session.execute(db.select(Courses).where(Courses.course_id == course_id)).scalar()
    #Se verifica si existe
    if not row:
        response_body['message'] = f'Curso {course_id} no encontrado'
        return response_body, 404

    if request.method == 'GET':
        response_body['results'] = row.serialize()
        response_body['message'] = f'Detalles del curso {course_id}'
        return response_body, 200
    
    if request.method == 'PUT':
        # Solo admin y profesor pueden actualizar cursos
        if not user['is_admin']:
            if user['role'] != 'teacher':
                response_body['message'] = 'No eres un Admin ni Teacher, no puedes actualizar cursos'
                return response_body, 403
            
        data = request.json
        # se valida que las claves requeridas estén en el request body
        if not data:
            response_body['message'] = 'Request body requerido para actualizar'
            return response_body, 400
        
        row.title = data.get('title', row.title)
        row.description = data.get('description', row.description)
        row.price = data.get('price', row.price)
        row.is_active = data.get('is_active', row.is_active)
        row.points = data.get('points', row.points)

        db.session.commit()
        response_body['results'] = row.serialize()
        response_body['message'] = f'Curso {course_id} Actualizado'
        return response_body, 200
    
    if request.method == 'DELETE':
        # Solo admin y profesor pueden eliminar cursos
        if not user.get('is_admin'):
            if user.get('role') != 'teacher':
                response_body['message'] = 'No eres un Admin ni Teacher, no puedes eliminar cursos'
                return response_body, 403
        db.session.delete(row)
        db.session.commit()
        response_body['message'] = f'Curso {course_id} Eliminado'
        return response_body, 200
    return response_body, 405

@api.route('/modules-public', methods=['GET'])
def modules_public():
    response_body = {}

    if request.method == 'GET':
        rows = db.session.execute(db.select(Modules)).scalars()
        results = [row.serialize() for row in rows]
        response_body['results'] = results
        response_body['message'] = 'Listado de módulos'
        return response_body, 200
    return response_body, 404

@api.route('/modules-private', methods=['GET', 'POST'])
@jwt_required()
def modules_private():
    response_body = {}

    # validacion de rol de usuario
    user = get_jwt()
    print(user)
    if not user.get('is_active'):
        response_body['message'] = 'Usuario no autorizado'
        return response_body, 403

    if request.method == 'GET':
        rows = db.session.execute(db.select(Modules)).scalars()
        results = [row.serialize() for row in rows]
        response_body['results'] = results
        response_body['message'] = 'Listado de módulos'
        return response_body, 200
    
    if request.method == 'POST':
        # Solo admin y profesor pueden crear Modulos
        if not user.get('is_admin'):
            if user.get('role') != 'teacher':
                response_body['message'] = 'No autorizado para crear módulos, no es admin ni teacher'
                return response_body, 403
        # Se valida que el request body no esté vacío
        data = request.json
        if not data:
            response_body['message'] = 'Request body requerido'
            return response_body, 400
        # se valida que las claves requeridas estén en el request body
        required_fields = ['title', 'order', 'points', 'course_id']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            response_body['message'] = 'Faltan campos requeridos'
            response_body['missing_fields'] = missing_fields
            return response_body, 400
        
        #Se verifica que el curso exista
        course = db.session.execute(
            db.select(Courses).where(Courses.id == data.get('course_id'))).scalar()
        if not course:
            response_body['message'] = 'Curso no encontrado'
            return response_body, 400
        
        row = Modules(title=data.get('title'),
                      order=data.get('order'),
                      points=data.get('points'),
                      course_id=data.get('course_id'),
                      created_by=user.get('email'))
        db.session.add(row)
        db.session.commit()

        response_body['results'] = row.serialize()
        response_body['message'] = 'Módulo creado'
        return response_body, 201
    return response_body, 405

@api.route('/modules/<int:module_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def module_private(module_id):
    response_body = {}
    # validacion de rol de usuario
    user = get_jwt()
    print(user)
    if not user.get('is_active'):
        response_body['message'] = 'Usuario no autorizado'
        return response_body, 403
    
    #Se busca el modulo por ID
    row = db.session.execute(
        db.select(Modules).where(Modules.module_id == module_id)).scalar()
    #Se verifica si existe
    if not row:
        response_body['message'] = 'Módulo no encontrado'
        return response_body, 404
    
    if request.method == 'GET':
        response_body['results'] = row.serialize()
        response_body['message'] = f'Detalles del módulo {module_id}'
        return response_body, 200
    
    if request.method == 'PUT':
        # Solo admin y profesor pueden actualizar modulos
        if not user.get('is_admin'):
            if user.get('role') != 'teacher':
                response_body['message'] = 'No eres un Admin ni Teacher, no puedes actualizar modulos'
                return response_body, 403
            
        data = request.json
        # se valida que las claves requeridas estén en el request body
        if not data:
            response_body['message'] = 'Request body requerido para actualizar'
            return response_body, 400
        
        # se verifica si se está actualizando el course_id
        if 'course_id' in data:
            course = db.session.execute(
                db.select(Courses).where(Courses.id == data.get('course_id'))
            ).scalar()
            if not course:
                response_body['message'] = 'Curso no encontrado'
                return response_body, 400
        # se verifica si se está actualizando el order
        target_course_id = data.get('course_id', row.course_id)
        
        if 'order' in data:
            existing_module = db.session.execute(
                db.select(Modules).where(Modules.course_id == target_course_id,
                                         Modules.order == data.get('order'),
                                         Modules.module_id != module_id)).scalar()
            if existing_module:
                response_body['message'] = f'Ya existe un módulo con el orden {data.get("order")} en este curso'
                return response_body, 400
        
        row.title = data.get('title', row.title)
        row.order = data.get('order', row.order)
        row.points = data.get('points', row.points)
        row.course_id = data.get('course_id', row.course_id)

        db.session.commit()
        response_body['results'] = row.serialize()
        response_body['message'] = f'Módulo {module_id} actualizado'
        return response_body, 200
    
    if request.method == 'DELETE':
        # Solo admin y profesor pueden eliminar Modulos
        if not user.get('is_admin'):
            if user.get('role') != 'teacher':
                response_body['message'] = 'No eres un Admin ni Teacher, no puedes eliminar Modulos'
                return response_body, 403
            
        db.session.delete(row)
        db.session.commit()
        response_body['message'] = f'Módulo {module_id} eliminado'
        return response_body, 200
    return response_body, 405

@api.route('/lessons-public', methods=['GET'])
def lessons_public():
    response_body = {}
    
    if request.method == 'GET':
        rows = db.session.execute(db.select(Lessons)).scalars()
        results = [row.serialize() for row in rows]
        response_body['results'] = results
        response_body['message'] = 'Listado de lecciones'
        return response_body, 200
    return response_body, 405

@api.route('/lessons-private', methods=['GET', 'POST'])
@jwt_required()
def lessons_private():
    response_body = {}

    # validacion de rol de usuario
    user = get_jwt()
    print(user)
    if not user.get('is_active'):
        response_body['message'] = 'Usuario no autorizado'
        return response_body, 403
    
    if request.method == 'GET':
        rows = db.session.execute(db.select(Lessons)).scalars()
        results = [row.serialize() for row in rows]
        response_body['results'] = results
        response_body['message'] = 'Listado de lecciones'
        return response_body, 200
    
    if request.method == 'POST':
        # Solo admin y profesor pueden crear lecciones
        if not user.get('is_admin'):
            if user.get('role') != 'teacher':
                response_body['message'] = 'No autorizado para crear lecciones, no es admin ni teacher'
                return response_body, 403
        # Se valida que el request body no esté vacío
        data = request.json
        if not data:
            response_body['message'] = 'Request body requerido'
            return response_body, 400
        # se valida que las claves requeridas estén en el request body
        required_fields = ['title', 'content', 'learning_objective', 'signs_taught', 'order', 'trial_version', 'module_id']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            response_body['message'] = 'Faltan campos requeridos'
            response_body['missing_fields'] = missing_fields
            return response_body, 400
        row = Lessons(title=data.get('title'),
                      content=data.get('content'),
                      learning_objective=data.get('learning_objective'),
                      signs_taught=data.get('signs_taught'),
                      order=data.get('order'),
                      trial_version=data.get('trial_version'),
                      module_id = data.get('module_id'),
                      created_by=user.get('email'))
                      
        db.session.add(row)
        db.session.commit()

        response_body['results'] = row.serialize()
        response_body['message'] = 'Lección creada'
        return response_body, 201
    return response_body, 405

@api.route('/lessons/<int:lesson_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def lesson_private(lesson_id):
    response_body = {}
        # validacion de rol de usuario
    user = get_jwt()
    print(user)
    if not user.get('is_active'):
        response_body['message'] = 'Usuario no autorizado'
        return response_body, 403
    
    #Se busca el curso por ID
    row = db.session.execute(
        db.select(Lessons).where(Lessons.lesson_id == lesson_id)).scalar()
    #Se verifica si existe
    if not row:
        response_body['message'] = f'Lección {lesson_id} no encontrada'
        return response_body, 404

    if request.method == 'GET':
        response_body['results'] = row.serialize()
        response_body['message'] = f'Detalles de la lección {lesson_id}'
        return response_body, 200
    
    if request.method == 'PUT':
        # Solo admin y profesor pueden actualizar lecciones
        if not user.get('is_admin'):
            if user.get('role') != 'teacher':
                response_body['message'] = 'No eres un Admin ni Teacher, no puedes actualizar lecciones'
                return response_body, 403
            
        data = request.json
        # se valida que las claves requeridas estén en el request body
        if not data:
            response_body['message'] = 'Request body requerido para actualizar'
            return response_body, 400
        
        #se verifica si se está actualizando el module_id
        if 'module_id' in data and data.get('module_id') != row.module_id:
            module = db.session.execute(db.select(Modules).where
                                        (Modules.id == data.get('module_id'))).scalar()
        if not module:
            response_body['message'] = 'Módulo no encontrado'
            return response_body, 400
          
        row.title = data.get('title', row.title)
        row.content = data.get('content', row.content)
        row.learning_objective = data.get('learning_objective', row.learning_objective)
        row.signs_taught = data.get('signs_taught', row.signs_taught)
        row.order = data.get('order', row.order)
        row.trial_version = data.get('trial_version', row.trial_version)
        row.module_id = data.get('module_id', row.module_id)

        db.session.commit()
        response_body['results'] = row.serialize()
        response_body['message'] = f'Lección {lesson_id} actualizada'
        return response_body, 200
    
    if request.method == 'DELETE':
        # Solo admin y profesor pueden eliminar lecciones
        if not user.get('is_admin'):
            if user.get('role') != 'teacher':
                response_body['message'] = 'No eres un Admin ni Teacher, no puedes eliminar lecciones'
                return response_body, 403
        db.session.delete(row)
        db.session.commit()
        response_body['message'] = f'Lección {lesson_id} eliminada'
        return response_body, 200
    return response_body, 405

@api.route('/purchases', methods=['GET', 'POST'])
@jwt_required()
def purchases():
    response_body = {}

    # validacion de rol de usuario
    user = get_jwt()
    print(user)
    if not user.get('is_active'):
        response_body['message'] = 'Usuario no autorizado'
        return response_body, 403
    
    if request.method == 'GET':
        # Solo el admin puede ver todas las compras realizadas 
        if not user.get('is_admin'):
            response_body['message'] = 'No autorizado para ver compras, no es admin'
            return response_body, 403
        rows = db.session.execute(db.select(Purchases)).scalars()
        results = [row.serialize() for row in rows]
        response_body['results'] = results
        response_body['message'] = 'Listado de compras'
        return response_body, 200

    if request.method == 'POST':
        #Cualquer usuario activo puede crear una compra para activar un curso o ampliar su suscripción
        # Se valida que el request body no esté vacío
        data = request.json
        if not data:
            response_body['message'] = 'Request body requerido'
            return response_body, 400
                # se valida que las claves requeridas estén en el request body
        required_fields = ['price', 'total', 'status', 'start_date', 'course_id', 'user_id', 'purchase_date']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            response_body['message'] = 'Faltan campos requeridos'
            response_body['missing_fields'] = missing_fields
            return response_body, 400
        #Se verifica que el curso exista o esta activo
        course = db.session.execute(db.select(Courses).where
                                   (Courses.id == data.get('course_id'),
                                    Courses.is_active == True)).scalar()
        if not course:
            response_body['message'] = 'Curso no encontrado'
            return response_body, 400
        #Validar que el usuario exista
    
        user_exists = db.session.execute(
            db.select(Users).where(Users.user_id == data.get('user_id'))).scalar()
        
        if not user_exists:
            response_body['message'] = 'Usuario no encontrado'
            return response_body, 400

        row = Purchases(purchase_date=data.get('purchase_date') or date.today(),
                        price=data.get('price'),
                        total=data.get('total'),
                        status=data.get('status'),
                        start_date=data.get('start_date'),
                        course_id=data.get('course_id'),
                        user_id=data.get('user_id'),
                        created_by=user.get('email'))
        db.session.add(row)
        db.session.commit()

        response_body['results'] = row.serialize()
        response_body['message'] = 'Compra creada'
        return response_body, 201
    return response_body, 405

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

@api.route('/user-points', methods=['GET', 'POST'])
def user_points():
    response_body = {}
    if request.method == 'GET':
        rows = db.session.execute(
        db.select(UserPoints) ).scalars()
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
    return response_body, 404

@api.route('/userprogress', methods=['GET', 'POST', 'DELETE'])
@jwt_required()
def userprogress():
    response_body = {}

    # Validación token / usuario activo
    user = get_jwt()
    if not user.get('is_active'):
        response_body['message'] = 'Usuario no autorizado'
        return response_body, 403

    current_user_id = user.get('user_id')
    role = user.get('role')
    is_admin = user.get('is_admin')

 
    # Método GET
    
    if request.method == 'GET':

        # Admin y teacher ven todo
        if is_admin or role == 'teacher':
            rows = db.session.execute(db.select(UserProgress)).scalars().all()
            response_body['results'] = [row.serialize() for row in rows]
            response_body['message'] = 'Listado general de progreso de todos los usuarios'
            return response_body, 200

        # Alumno ve solo su progreso
        rows = db.session.execute(
            db.select(UserProgress).where(UserProgress.user_id == current_user_id)).scalars().all()

        response_body['results'] = [row.serialize() for row in rows]
        response_body['message'] = f'Listado de progreso del usuario {current_user_id}'
        return response_body, 200

    # POST
    
    if request.method == 'POST':
        data = request.json
        if not data:
            response_body['message'] = 'Request body requerido'
            return response_body, 400

        required_fields = ['lesson_id', 'user_id', 'completed', 'start_date']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            response_body['message'] = 'Faltan campos requeridos'
            response_body['missing_fields'] = missing_fields
            return response_body, 400

        target_user_id = data.get('user_id')

        # Alumno solo puede crear para sí mismo
        if not is_admin and role != 'teacher':
            if target_user_id != current_user_id:
                response_body['message'] = 'No autorizado para crear progreso de otro usuario'
                return response_body, 403

        # Validación boolean
        if not isinstance(data.get('completed'), bool):
            response_body['message'] = "completed debe ser boolean (true/false)"
            return response_body, 400

        # (Recomendado) evitar duplicados: mismo user_id + lesson_id
        existing = db.session.execute(
            db.select(UserProgress).where(
                UserProgress.user_id == target_user_id,
                UserProgress.lesson_id == data.get('lesson_id')) ).scalar()

        if existing:
            response_body['message'] = 'Ya existe un progreso para este usuario en esta lección'
            response_body['results'] = existing.serialize()
            return response_body, 400

        # Crear progreso
        row = UserProgress(
            user_id=target_user_id,
            lesson_id=data.get('lesson_id'),
            completed=data.get('completed'),
            start_date=data.get('start_date'),
            completion_date=data.get('completion_date'))

        db.session.add(row)
        db.session.commit()

        response_body['results'] = row.serialize()
        response_body['message'] = 'Progreso creado'
        return response_body, 201

     #  Método DELETE
   
    if request.method == 'DELETE':

        # Solo admin o teacher pueden borrar progreso
        if not is_admin and role != 'teacher':
            response_body['message'] = 'No autorizado para eliminar progreso'
            return response_body, 403

        data = request.json
        if not data:
            response_body['message'] = 'Request body requerido para eliminar progreso'
            return response_body, 400

        required_fields = ['user_id', 'lesson_id']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            response_body['message'] = 'Faltan campos requeridos'
            response_body['missing_fields'] = missing_fields
            return response_body, 400

        row = db.session.execute(
            db.select(UserProgress).where(
                UserProgress.user_id == data.get('user_id'),
                UserProgress.lesson_id == data.get('lesson_id') )).scalar()

        if not row:
            response_body['message'] = 'Progreso no encontrado'
            return response_body, 404

        db.session.delete(row)
        db.session.commit()

        response_body['message'] = 'Progreso eliminado'
        return response_body, 200

    return response_body, 405




@api.route('/userprogress/<int:lesson_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def userprogress_detail(lesson_id):
    response_body = {}

    user = get_jwt()

    # Usuario activo
    if not user.get('is_active'):
        response_body['message'] = 'Usuario no autorizado'
        return response_body, 403

    current_user_id = user.get('user_id')
    role = user.get('role')
    is_admin = user.get('is_admin')

    # Buscar progreso
    row = db.session.execute(
        db.select(UserProgress).where(
            UserProgress.lesson_id == lesson_id,
            UserProgress.user_id == current_user_id ) ).scalar()

    if not row:
        response_body['message'] = 'Progreso de usuario no encontrado'
        return response_body, 404

     # GET
    
    if request.method == 'GET':

        result = fix_datetime(row.serialize())

        response_body['results'] = result
        response_body['message'] = f'Detalles del progreso para lesson_id {lesson_id}'

        return response_body, 200

    # Alumno NO puede modificar
    if role == 'alumno':
        response_body['message'] = 'Acceso denegado: Los alumnos no pueden modificar o eliminar progresos'
        return response_body, 403

    if not is_admin and role != 'teacher':
        response_body['message'] = 'Rol no autorizado'
        return response_body, 403

   # Método  PUT
   
    if request.method == 'PUT':
        data = request.json

        if not data:
            response_body['message'] = 'No se enviaron datos para actualizar'
            return response_body, 400

        if 'completed' in data and not isinstance(data.get('completed'), bool):
            response_body['message'] = 'completed debe ser true o false'
            return response_body, 400

        row.completed = data.get('completed', row.completed)
        row.start_date = data.get('start_date', row.start_date)
        row.completion_date = data.get('completion_date', row.completion_date)

        db.session.commit()

        result = fix_datetime(row.serialize())

        response_body['results'] = result
        response_body['message'] = f'Progreso actualizado para lesson_id {lesson_id}'

        return response_body, 200

   # Método DELETE
   
    if request.method == 'DELETE':
        db.session.delete(row)
        db.session.commit()

        response_body['message'] = f'Progreso eliminado para lesson_id {lesson_id}'

        return response_body, 200

    return response_body, 405

    
    
@api.route('/achievements', methods=['GET', 'POST'])
def achievements():
    response_body = {}

    # Método GET
    
    if request.method == 'GET':

        rows = db.session.execute( db.select(Achievements) ).scalars().all()

        response_body['results'] = [row.serialize() for row in rows]
        response_body['message'] = 'Listado de logros'

        return response_body, 200

    # Método POST
  
    if request.method == 'POST':

        data = request.json

        if not data:
            response_body['message'] = 'Request body requerido'
            return response_body, 400

        required_fields = ['name', 'description', 'required_points']
        missing_fields = [f for f in required_fields if f not in data]

        if missing_fields:
            response_body['message'] = 'Faltan campos requeridos'
            response_body['missing_fields'] = missing_fields
            return response_body, 400

        # VALIDACIÓN 
        if not isinstance(data.get('required_points'), int):
            response_body['message'] = 'required_points debe ser un número entero'
            return response_body, 400

        row = Achievements(
            name=data.get('name'),
            description=data.get('description'),
            required_points=data.get('required_points') )

        db.session.add(row)
        db.session.commit()

        response_body['results'] = row.serialize()
        response_body['message'] = 'Logro creado'

        return response_body, 201

    return response_body, 405


@api.route('/achievements/<int:achievement_id>', methods=['GET', 'PUT', 'DELETE'])
def achievement(achievement_id):
    response_body = {}

    # Buscar logro por ID
    row = db.session.execute(
        db.select(Achievements).where(Achievements.achievement_id == achievement_id) ).scalar()

    if not row:
        response_body['message'] = 'Logro no encontrado'
        return response_body, 404

    # GET
   
    if request.method == 'GET':
        response_body['results'] = row.serialize()
        response_body['message'] = f'Detalles del logro {achievement_id}'
        return response_body, 200

   # PUT
   
    if request.method == 'PUT':
        data = request.json

        if not data:
            response_body['message'] = 'Request body requerido para actualizar'
            return response_body, 400

        allowed_fields = ['name', 'description', 'required_points', 'icon']
        invalid_fields = [k for k in data.keys() if k not in allowed_fields]

        if invalid_fields:
            response_body['message'] = 'Campos no permitidos'
            response_body['invalid_fields'] = invalid_fields
            response_body['allowed_fields'] = allowed_fields
            return response_body, 400

        # Validación de tipo para required_points
        if 'required_points' in data and not isinstance(data.get('required_points'), int):
            response_body['message'] = 'required_points debe ser un número entero'
            return response_body, 400

        row.name = data.get('name', row.name)
        row.description = data.get('description', row.description)
        row.required_points = data.get('required_points', row.required_points)
        row.icon = data.get('icon', row.icon)

        db.session.commit()

        response_body['results'] = row.serialize()
        response_body['message'] = f'Logro {achievement_id} actualizado'
        return response_body, 200

  # DELETE
   
    if request.method == 'DELETE':
        db.session.delete(row)
        db.session.commit()

        response_body['message'] = f'Logro {achievement_id} eliminado'
        return response_body, 200

    return response_body, 405


@api.route('/user-achievements', methods=['GET', 'POST'])
def user_achievements():
    response_body = {}
# validacion de rol de usuario
    user = get_jwt()
    print(user)

    if not user.get('is_active'):
        response_body['message'] = 'Usuario no autorizado'
        return response_body, 403

    # GET 
    if request.method == 'GET':

        # Alumno solo puede ver sus propios logros
        if user.get('role') == 'alumno':
            rows = db.session.execute(
                db.select(UserAchievements).where(
                    UserAchievements.user_id == user.get('id') )).scalars().all()
        else:
            # Admin y Teacher ven todos
            rows = db.session.execute(
                db.select(UserAchievements)).scalars().all()

        results = [row.serialize() for row in rows]

        response_body['results'] = results
        if not results or len(results) == 0:
            response_body['message'] = 'No hay logros obtenidos por usuarios aún'
        else:
            response_body['message'] = 'Listado de logros obtenidos por usuarios'

        return response_body, 200

    # POST 
    if request.method == 'POST':

        # Solo admin y teacher pueden asignar logros
        if not user.get('is_admin'):
            if user.get('role') != 'teacher':
                response_body['message'] = (
                    'No eres Admin ni Teacher, no puedes asignar logros' )
                return response_body, 403

        data = request.json

        if not data:
            response_body['message'] = 'Request body requerido para asignar logro'
            return response_body, 400

        if not data.get('user_id') or not data.get('achievement_id'):
            response_body['message'] = 'user_id y achievement_id son obligatorios'
            return response_body, 400

        row = UserAchievements(
            user_id=data.get('user_id'),
            achievement_id=data.get('achievement_id'),
            obtained_date=data.get('obtained_date'))

        db.session.add(row)
        db.session.commit()

        response_body['results'] = row.serialize()
        response_body['message'] = 'Logro asignado al usuario'
        return response_body, 201

    return response_body, 405

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
    return response_body, 404

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
    return response_body, 404


