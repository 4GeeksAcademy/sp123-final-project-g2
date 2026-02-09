"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from flask import Flask, request, Blueprint
from sqlalchemy import func
from api.models import UserProgress, db, Users, Courses, Modules, Purchases, MultimediaResources, Lessons, Achievements, UserPoints, UserAchievements
from api.utils import generate_sitemap, APIException
from flask_cors import CORS

from werkzeug.security import check_password_hash 
from werkzeug.security import generate_password_hash

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt

from datetime import datetime, timezone, timedelta




CURRENT_USER_ID = 1

api = Blueprint('api', __name__)
CORS(api)  # Allow CORS requests to this API

""" --- HELPERS DE VALIDACIÓN --- """

# Helper para validar que el usuario del JWT esté activo
def validate_active_user():

    user = get_jwt()
    
    if not user:
        response_body = {
            'results': {},
            'message': 'Token inválido o no proporcionado'
        }
        return None, response_body, 401
    
    if not user.get('is_active', False):
        response_body = {
            'results': {},
            'message': 'Usuario no autorizado'
        }
        return None, response_body, 403
    
    # se verifica si el usuario es demo y se valida su trial_end_date
    trial_date_parseable = False
    
    if user.get('role') == 'demo':
        trial_end_date = user.get('trial_end_date')
        
        # Validar que exista y sea string
        if trial_end_date and isinstance(trial_end_date, str) and trial_end_date.strip():
    
            # Verificar formato ISO básico
            if 'T' in trial_end_date and '-' in trial_end_date:
                try:
                    # Intentar parsear para verificar validez
                    date_str = trial_end_date.replace('Z', '+00:00')
                    trial_end = datetime.fromisoformat(date_str)
                    trial_date_parseable = True  # ✅ FLAG: fecha es parseable
                    
                    # Validar que trial no haya expirado
                    now = datetime.now(timezone.utc)
                    if trial_end < now:
                        response_body = {
                            'results': {},
                            'message': 'Periodo de trial expirado. Por favor, actualice su plan.'
                        }
                        return None, response_body, 403
                        
                except ValueError:
                    print(f"⚠️ ADVERTENCIA: Formato trial_end_date inválido para usuario {user.get('user_id')}: {trial_end_date}")
                    
    # Se agrega el flag de parseabilidad al objeto user para uso posterior (ejemplo: en /protected para mostrar info del trial)
    user['_trial_date_parseable'] = trial_date_parseable
    
    return user, None, 200

# helper para validar el rol del usuario y permisos de admin, con opciones flexibles para diferentes escenarios de autorización
def validate_user_role(
    require_role=None,
    allowed_roles=None,
    require_admin=False,
    allow_demo=False
):
    # 1. Validar usuario activo
    user, response_body, status_code = validate_active_user()
    if response_body:
        return None, response_body, status_code
    
    # 2. Extraer datos del usuario
    user_role = user.get('role')
    is_admin = user.get('is_admin', False)
    
    # 3. Validar permisos de admin si se requieren
    if require_admin:
        if not is_admin:
            response_body = {
                'results': {},
                'message': 'Se requieren permisos de administrador'
            }
            return None, response_body, 403
        return user, None, 200
    
    # 4. Admin tiene acceso total
    if is_admin:
        return user, None, 200
    
    # 5. Validar acceso para usuarios demo
    if user_role == 'demo' and not allow_demo:
        response_body = {
            'results': {},
            'message': 'Usuarios demo tienen acceso limitado'
        }
        return None, response_body, 403
    
    # 6. Validar rol específico requerido
    if require_role is not None:
        if user_role != require_role:
            response_body = {
                'results': {},
                'message': f'Se requiere rol de {require_role}'
            }
            return None, response_body, 403
        return user, None, 200
    
    # 7. Validar lista de roles permitidos
    if allowed_roles is not None:
        if user_role not in allowed_roles:
            if len(allowed_roles) == 1:
                msg = f'Se requiere rol de {allowed_roles[0]}'
            else:
                msg = f'Se requiere uno de estos roles: {", ".join(allowed_roles)}'
            
            response_body = {
                'results': {},
                'message': msg
            }
            return None, response_body, 403
        return user, None, 200
    
    # 8. Si no hay restricciones, acceso concedido
    return user, None, 200

#helper para validar que el request tenga un body en formato JSON y que contenga los campos requeridos (si se especifican)
def validate_request_json(required_fields=None):
    
    # Se verifica que el request tenga un body en formato JSON
    if not request.json: 
        response_body = {
            'message': 'Request body requerido. Envía los datos en formato JSON.',
            'results': {}
        }
        return None, response_body, 400
    
    # Se obtienen los datos del JSON del request
    received_data = request.json 
    
    # Se valida que los campos requeridos estén presentes en el JSON recibido
    if required_fields:
        missing_fields = []
        
        # Se recorre la lista de campos requeridos y se verifica si cada uno está presente en los datos recibidos
        for field in required_fields:
            if field not in received_data:
                missing_fields.append(field)
        
        # Dado que falte algun campo requerido se construye un response_body indicando el error y cuáles campos faltan, y se retorna con status 400
        if missing_fields:
            response_body = {
                'message': 'Faltan campos requeridos en los datos',
                'results': {},
                'missing_fields': missing_fields 
            }
            return None, response_body, 400
    
    return received_data, None, 200

# Helper que combina validación de JSON y campos requeridos para endpoints POST/PUT
def validate_required_data(data, required_fields):

    if not data:
        response_body = {
            'results': {},
            'message': 'Datos no proporcionados'
        }
        return None, response_body, 400  
    
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        response_body = {
            'results': {},
            'message': 'Faltan campos requeridos',
            'missing_fields': missing_fields
        }
        return None, response_body, 400 
    
    return data, None, 200

# Obtiene la información del período de prueba para usuarios demo, verificando que sean demo y tengan fecha válida.
def get_trial_info(user):

    #  Solo para usuarios demo
    if user.get('role') != 'demo':
        return None
    
    # Obtener fecha de trial
    trial_end_date = user.get('trial_end_date')
    
    #  Validaciones básicas
    if not trial_end_date or not isinstance(trial_end_date, str):
        return None
    
    if not trial_end_date.strip():
        return None
    
    # Se verifica que la fecha tenga el formato correcto (como "2024-12-31T23:59:59"), para evitar errores al procesarla.
    if not user.get('_trial_date_parseable', False):
        return None
    
    # Se ajusta la fecha al formato estándar y se convierte a un objeto de fecha, sabiendo que ya fue validada antes y funcionará correctamente.
    date_str = trial_end_date.replace('Z', '+00:00')
    trial_end = datetime.fromisoformat(date_str)
    now = datetime.now(timezone.utc)
    
    # 6. Calcular información
    days_left = (trial_end - now).days
    
    return {
        'trial_end_date': trial_end_date,
        'days_remaining': max(days_left, 0),
        'status': 'active' if days_left > 0 else 'expired'
    }


""" --- RUTAS  --- """


@api.route("/login", methods=["POST"])
def login():
    # 1. Validar JSON y campos requeridos
    data, response_body, status = validate_request_json(["email", "password"])
    if response_body:
        return response_body, status 
    
    # Se obtienen email y contraseña del JSON recibido, y se normaliza el email para evitar problemas de mayúsculas/minúsculas o espacios.
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    
    # 3. Validar contraseña no vacía
    if not password:
        response_body = {
            'message': "El usuario debe proporcionar una contraseña",
            'results': {}
        }
        return response_body, 400
    
    # 4. Buscar usuario activo
    row = db.session.execute(db.select(Users).where(Users.email == email,Users.is_active == True)).scalar()
    
    # 5. Respuesta segura 
    if not row or not check_password_hash(row.password_hash, password):
        response_body = {
            'message': "Correo o contraseña incorrectos, o usuario inactivo",
            'results': {}
        }
        return response_body, 401
    
    # 6. Crear token con datos de usuario
    user_data = {
        'user_id': row.user_id,
        'is_active': row.is_active,
        'role': row.role,
        'is_admin': row.is_admin,
        'trial_end_date': row.trial_end_date.isoformat() if row.trial_end_date else None 
    }
    
    response_body = {
        'message': 'Usuario autenticado correctamente',
        'results': {
            'user_id': user_data['user_id'],
            'role': user_data['role'],
            'is_active': user_data['is_active'],
            'is_admin': user_data['is_admin'],
            'trial_end_date': user_data['trial_end_date']
        },
        'access_token': create_access_token(
            identity=user_data['user_id'], 
            additional_claims=user_data
        )
    }
    return response_body, 200

@api.route("/protected", methods=["GET"])
@jwt_required()
def protected():

    # Se valida que el usuario del JWT esté activo con el helper correspondiente, y se obtienen sus datos para incluirlos en la respuesta.
    user, response_body, status_code = validate_active_user()
    if response_body:
        return response_body, status_code
    
    # Construir datos base del usuario
    response_data = {
        'user_id': user.get('user_id'),
        'email': user.get('email', ''),
        'role': user.get('role'),
        'is_active': user.get('is_active', False),
        'is_admin': user.get('is_admin', False)
    }
    
    #  Obtener información de trial si aplica (usando helper)
    trial_info = get_trial_info(user)
    if trial_info:
        response_data['trial_info'] = trial_info
    
    # 4. Construir y retornar respuesta final
    response_body = {
        'message': 'Acceso autorizado a información protegida',
        'results': response_data
    }
    
    return response_body, 200

@api.route('/register', methods=['POST'])
def register():
    response_body = {}
    
    # 1. Validar JSON y campos requeridos
    data, error_response, status = validate_request_json([
        'email', 'password', 'first_name', 'last_name'
    ])
    if error_response:
        return error_response, status
    
    # 2. Validar formato de email
    email = data.get('email', '').strip().lower()
    if '@' not in email or '.' not in email.split('@')[-1]:
        response_body = {
            'message': 'Formato de email inválido',
            'results': {}
        }
        return response_body, 400
    
    # 3. Validar contraseña
    password = data.get('password', '')
    if not password:
        response_body = {
            'message': 'La contraseña no puede estar vacía',
            'results': {}
        }
        return response_body, 400
    
    if len(password) < 8:
        response_body = {
            'message': 'La contraseña debe tener al menos 8 caracteres',
            'results': {}
        }
        return response_body, 400
    
    # 4. Se verifica si ya existe un usuario con el mismo email (sin importar mayúsculas/minúsculas)
    existing_user = db.session.execute(db.select(Users).where(Users.email == email)).scalar()
    
    # Si el usuario ya existe, informar error
    if existing_user:
        response_body = {
            'message': f'El usuario con email {email} ya existe',
            'results': {}
        }
        return response_body, 409
    
    # 5. Si el usuario no exite se crea un nuevo usuario con rol demo, trial de 7 días, y se guarda en la base de datos. Se utiliza generate_password_hash para almacenar la contraseña de forma segura.
    now = datetime.now(timezone.utc)
    trial_end_date = now + timedelta(days=7)
    
    password_hash = generate_password_hash(password)
    
    row = Users(
        email=email,
        password_hash=password_hash,
        first_name=data.get('first_name', '').strip(),
        last_name=data.get('last_name', '').strip(),
        role='demo',
        current_points=0,
        is_active=True,
        is_admin=False,
        registration_date=now,
        trial_end_date=trial_end_date,
        last_access=None
    )
    
    db.session.add(row)
    db.session.commit() 
    
    response_body['message'] = 'Usuario demo creado exitosamente. Trial de 7 días activado.'
    response_body['results'] = {
        'user_id': row.user_id,
        'email': row.email,
        'first_name': row.first_name,
        'last_name': row.last_name,
        'role': row.role,
        'trial_end_date': trial_end_date.isoformat()
    }
    
    
    return response_body, 201


@api.route('/users', methods=['GET'])
@jwt_required()
def get_users():

    response_body = {}
    
    # Validar usuario activo y obtener datos del JWT con el helper correspondiente
    user, response_body_validation, status = validate_active_user()
    if response_body_validation:
        return response_body_validation, status
    
    user_role = user.get('role')
    is_admin = user.get('is_admin', False)
    teacher_id = user.get('user_id')
    
    # Obtener parámetros de paginación
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=20, type=int)
    
    # Validar parámetros de paginación
    if page < 1:
        page = 1
    if per_page < 1 or per_page > 100:  
        per_page = 20
    
    # Calcular offset para paginación
    offset = (page - 1) * per_page
    
    # Admin ve todos los usuarios (todos los campos)
    if is_admin:
        # Contar total de usuarios para paginación
        total_query = db.session.execute(db.select(db.func.count()).select_from(Users)).scalar()
        
        # Obtener usuarios con paginación
        rows = db.session.execute(db.select(Users).order_by(Users.user_id).limit(per_page).offset(offset)).scalars()
        
        results = [row.serialize() for row in rows]
        
        # Calcular páginas totales de forma segura
        total_pages = 0
        if per_page > 0 and total_query:
            total_pages = (total_query + per_page - 1) // per_page
        
        response_body['message'] = 'Listado completo de usuarios (vista admin)'
        response_body['pagination'] = {
            'page': page,
            'per_page': per_page,
            'total': total_query,
            'total_pages': total_pages
        }
    
    # Teacher ve solo estudiantes de SUS cursos (campos limitados: nombre, email, puntos)
    elif user_role == 'teacher':
        # Buscar estudiantes en cursos del profesor
        students_query = db.session.execute(
            db.select(Users)
            .join(Purchases, Users.user_id == Purchases.user_id)
            .join(Courses, Purchases.course_id == Courses.course_id)
            .where(Courses.created_by == teacher_id, Users.role == 'student')
            .distinct()
            .order_by(Users.user_id)
            .limit(per_page)
            .offset(offset)
        ).scalars()
        
        # Contar total (para paginación)
        total_count_query = db.session.execute(
            db.select(db.func.count()).select_from(Users)
            .join(Purchases, Users.user_id == Purchases.user_id)
            .join(Courses, Purchases.course_id == Courses.course_id)
            .where(Courses.created_by == teacher_id, Users.role == 'student')
            .distinct()
        ).scalar()
        
        students = list(students_query)
        
        # Solo campos permitidos: nombre, email, puntos
        results = []
        for student in students:
            results.append({
                'user_id': student.user_id,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'email': student.email,
                'current_points': student.current_points,
                'role': student.role,
            })
        
        # Calcular páginas totales de forma segura
        total_pages = 0
        if per_page > 0 and total_count_query:
            total_pages = (total_count_query + per_page - 1) // per_page
        
        response_body['message'] = f'Estudiantes en tus cursos ({len(results)} estudiantes)'
        response_body['pagination'] = {
            'page': page,
            'per_page': per_page,
            'total': total_count_query or 0,
            'total_pages': total_pages
        }
    
    # Student/Demo no puede ver lista de usuarios
    else:
        response_body = {
            'message': 'No autorizado para ver listado de usuarios',
            'results': {}
        }
        return response_body, 403
    
    response_body['results'] = results
    response_body['count'] = len(results)
    
    return response_body, 200

@api.route('/users/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def user(user_id):
    response_body = {}
    
    # 1. Validar usuario autenticado
    current_user, response_body_validation, status = validate_active_user()
    if response_body_validation:
        return response_body_validation, status
    
    current_user_id = current_user.get('user_id')
    is_admin = current_user.get('is_admin', False)
    
    # 2. Buscar usuario objetivo
    target_user = db.session.execute(
        db.select(Users).where(Users.user_id == user_id)
    ).scalar()
    
    if not target_user:
        response_body = {
            'message': f'Usuario {user_id} no encontrado',
            'results': {}
        }
        return response_body, 404
    
    # 3. GET: Obtener detalles
    if request.method == 'GET':
        if not is_admin and current_user_id != user_id:
            response_body = {
                'message': 'No autorizado para ver este usuario',
                'results': {}
            }
            return response_body, 403
        
        if is_admin:
            user_data = target_user.serialize()
        else:
            user_data = {
                'user_id': target_user.user_id,
                'first_name': target_user.first_name,
                'last_name': target_user.last_name,
                'email': target_user.email,
                'role': target_user.role,
                'current_points': target_user.current_points,
                'is_active': target_user.is_active,
                'registration_date': target_user.registration_date.isoformat() if target_user.registration_date else None,
                'trial_end_date': target_user.trial_end_date.isoformat() if target_user.trial_end_date else None,
            }
        
        response_body = {
            'message': f'Detalles del usuario {user_id}',
            'results': user_data
        }
        return response_body, 200
    
    # 4. PUT: Actualizar usuario
    if request.method == 'PUT':
        if not is_admin and current_user_id != user_id:
            response_body = {
                'message': 'No autorizado para actualizar este usuario',
                'results': {}
            }
            return response_body, 403
        
        data, error_response, status = validate_request_json()
        if error_response:
            return error_response, status
        
        # Campos que solo admin puede modificar (email YA NO está aquí)
        admin_only_fields = ['is_admin', 'role', 'current_points', 'trial_end_date', 'is_active']
        if not is_admin:
            for field in admin_only_fields:
                if field in data:
                    response_body = {
                        'message': f'No autorizado para modificar {field}',
                        'results': {}
                    }
                    return response_body, 403
        
        # Validar email único (si se está actualizando) - AHORA usuarios pueden cambiar su email
        if 'email' in data and data['email'] != target_user.email:
            existing = db.session.execute(
                db.select(Users).where(Users.email == data['email'])
            ).scalar()
            if existing:
                response_body = {
                    'message': 'El email ya está registrado',
                    'results': {}
                }
                return response_body, 409
        
        # Actualizar campos
        if 'first_name' in data:
            target_user.first_name = data['first_name'].strip()
        if 'last_name' in data:
            target_user.last_name = data['last_name'].strip()
        if 'email' in data:  # ✅ AHORA usuarios pueden cambiar su email
            target_user.email = data['email'].strip().lower()
        if 'role' in data and is_admin:
            target_user.role = data['role']
        if 'current_points' in data and is_admin:
            points = data['current_points']
            if isinstance(points, (int, float)) and points >= 0:
                target_user.current_points = points
            else:
                response_body = {
                    'message': 'Los puntos deben ser un número no negativo',
                    'results': {}
                }
                return response_body, 400
        if 'is_active' in data and is_admin:
            target_user.is_active = bool(data['is_active'])
        if 'is_admin' in data and is_admin:
            target_user.is_admin = bool(data['is_admin'])
        if 'trial_end_date' in data and is_admin:
            try:
                from datetime import datetime
                trial_date = datetime.fromisoformat(data['trial_end_date'].replace('Z', '+00:00'))
                target_user.trial_end_date = trial_date
            except ValueError:
                response_body = {
                    'message': 'Formato de fecha inválido para trial_end_date',
                    'results': {}
                }
                return response_body, 400
        
        db.session.commit()
        
        if is_admin:
            response_data = target_user.serialize()
        else:
            response_data = {
                'user_id': target_user.user_id,
                'first_name': target_user.first_name,
                'last_name': target_user.last_name,
                'email': target_user.email,
                'role': target_user.role,
                'current_points': target_user.current_points,
                'is_active': target_user.is_active,
                'registration_date': target_user.registration_date.isoformat() if target_user.registration_date else None,
                'trial_end_date': target_user.trial_end_date.isoformat() if target_user.trial_end_date else None,
            }
        
        response_body = {
            'message': f'Usuario {user_id} actualizado',
            'results': response_data
        }
        return response_body, 200
    
    # 5. DELETE: Eliminar usuario
    if request.method == 'DELETE':
        if not is_admin:
            response_body = {
                'message': 'Solo administradores pueden eliminar usuarios',
                'results': {}
            }
            return response_body, 403
        
        if current_user_id == user_id:
            response_body = {
                'message': 'No puedes eliminarte a ti mismo',
                'results': {}
            }
            return response_body, 400
        
        db.session.delete(target_user)
        db.session.commit()
        
        response_body = {
            'message': f'Usuario {user_id} eliminado',
            'results': {}
        }
        return response_body, 200
    
    return response_body, 405

@api.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():

    response_body = {}
    
    #Validar usuario autenticado y obtener datos del JWT con el helper correspondiente
    user, response_body_validation, status = validate_active_user()
    if response_body_validation:
        return response_body_validation, status
    
    user_id = user.get('user_id')
    
    # Valida el JSON y campos requeridos con el helper correspondiente
    data, error_response, status = validate_request_json(['current_password', 'new_password'])
    if error_response:
        return error_response, status
    
    # se buscar usuario en base de datos
    db_user = db.session.execute(db.select(Users).where(Users.user_id == user_id)).scalar()
    
    if not db_user:
        response_body['message'] = 'Usuario no encontrado'
        return response_body, 404
    
    # Se obtienen las contraseñas del request
    current_password = data.get('current_password', '')
    new_password = data.get('new_password', '')
    
    # Se verifica que la contraseña actual sea correcta usando check_password_hash para comparar con el hash almacenado en la base de datos
    if not check_password_hash(db_user.password_hash, current_password):
        response_body['message'] = 'Contraseña actual incorrecta'
        return response_body, 401
    
    # Se validan las reglas de la nueva contraseña (ejemplo: no vacía, mínimo 8 caracteres)
    if not new_password:
        response_body['message'] = 'La nueva contraseña no puede estar vacía'
        return response_body, 400
    
    if len(new_password) < 8:
        response_body['message'] = 'La nueva contraseña debe tener al menos 8 caracteres'
        return response_body, 400
    
    # Se verifica que la nueva contraseña no sea igual a la anteriror
    if check_password_hash(db_user.password_hash, new_password):
        response_body['message'] = 'La nueva contraseña no puede ser igual a la actual'
        return response_body, 400
    
    
    db_user.password_hash = generate_password_hash(new_password)
    db.session.commit()
    
    response_body['message'] = 'Contraseña actualizada exitosamente'
    response_body['results'] = {
        'user_id': user_id,
        'password_changed': True
    }
    
    return response_body, 200

@api.route('/delete-my-account', methods=['POST'])
@jwt_required()
def delete_my_account():

    response_body = {}
    
    # Se valida usuario autenticado y obtener datos del JWT con el helper correspondiente
    user, response_body_validation, status = validate_active_user()
    if response_body_validation:
        return response_body_validation, status
    
    user_id = user.get('user_id')
    
    # Se valida el JSON y campos requeridos con el helper correspondiente 
    data, error_response, status = validate_request_json(['password', 'confirmation'])
    if error_response:
        return error_response, status
    
    # Se busca el usuario en base de datos
    db_user = db.session.execute(db.select(Users).where(Users.user_id == user_id)).scalar()
    
    if not db_user:
        response_body['message'] = 'Usuario no encontrado'
        return response_body, 404
    
    # Se obtienen datos de confirmación
    password = data.get('password', '')
    confirmation = data.get('confirmation', '').strip().lower()
    
    # Se verifica la contrasela del usuario 
    if not check_password_hash(db_user.password_hash, password):
        response_body['message'] = 'Contraseña incorrecta'
        return response_body, 401
    
    # Se verifica el texto de confirmacion 
    if confirmation != 'eliminar mi cuenta':
        response_body['message'] = 'Debes escribir "eliminar mi cuenta" para confirmar'
        return response_body, 400
    
    # Se elimina la cuenta de forma segura (desactivando el usuario, modificando el email para evitar conflictos futuros, y guardando la fecha de eliminación)
    db_user.is_active = False
    db_user.email = f"deleted_{user_id}_{db_user.email}"
    db_user.deleted_at = datetime.now(timezone.utc)
    
    db.session.commit()
    
    response_body['message'] = 'Cuenta eliminada exitosamente'
    response_body['results'] = {
        'account_deleted': True,
        'user_id': user_id,
        'deleted_at': datetime.now(timezone.utc).isoformat()
    }
    
    return response_body, 200

@api.route('/courses-public', methods=['GET'])
def courses_public():
    response_body = {}

    if request.method == 'GET':
        # Obtener parámetros de paginación
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=20, type=int)
        
        # Validar parámetros
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 20
        
        # Calcular offset
        offset = (page - 1) * per_page
        
        # Contar total de cursos activos
        total_query = db.session.execute(
            db.select(db.func.count()).select_from(Courses)
            .where(Courses.is_active == True)
        ).scalar()
        
        # Obtener cursos con paginación
        rows = db.session.execute(
            db.select(Courses)
            .where(Courses.is_active == True)
            .order_by(Courses.course_id)
            .limit(per_page)
            .offset(offset)
        ).scalars()
        
        results = [row.serialize() for row in rows]
        
        # Calcular páginas totales
        total_pages = 0
        if per_page > 0 and total_query:
            total_pages = (total_query + per_page - 1) // per_page
        
        response_body['results'] = results
        response_body['message'] = 'Listado de cursos'
        response_body['count'] = len(results)
        response_body['pagination'] = {
            'page': page,
            'per_page': per_page,
            'total': total_query,
            'total_pages': total_pages
        }
        
        return response_body, 200
    
    return response_body, 405

@api.route('/courses-private', methods=['GET', 'POST'])
@jwt_required()
def courses_private():
    response_body = {}

    # 1. Validar usuario autenticado y obtener datos del JWT con el helper correspondiente
    user, response_body_validation, status = validate_active_user()
    if response_body_validation:
        return response_body_validation, status
    
    is_admin = user.get('is_admin', False)
    user_role = user.get('role')
    user_id = user.get('user_id')
    
    if request.method == 'GET':
        # Obtener parámetros de paginación del request
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=20, type=int)
        
        # Validar parámetros
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 20
        
        offset = (page - 1) * per_page
        
        # Se cuenta el tototal de cursos para la pagainación
        total_query = db.session.execute(db.select(db.func.count()).select_from(Courses)).scalar()
        
        # Obtener cursos con paginación
        rows = db.session.execute(db.select(Courses).order_by(Courses.course_id).limit(per_page).offset(offset)).scalars()
        
        results = [row.serialize() for row in rows]
        
        # Calcular páginas totales
        total_pages = 0
        if per_page > 0 and total_query:
            total_pages = (total_query + per_page - 1) // per_page
        
        response_body['message'] = 'Listado de cursos (privado)'
        response_body['count'] = len(results)
        response_body['results'] = results
        response_body['pagination'] = {
            'page': page,
            'per_page': per_page,
            'total': total_query,
            'total_pages': total_pages
        }
        
        return response_body, 200

    if request.method == 'POST':
        # Solo admin y profesor pueden crear cursos
        if not is_admin and user_role != 'teacher':
            response_body['results'] = {}
            response_body['message'] = 'No autorizado para crear cursos, no es Administrador ni profesor'
            return response_body, 403
        
        # Validar JSON y campos requeridos
        data, error_response, status = validate_request_json(['title', 'price', 'points'])
        if error_response:
            return error_response, status
        
        # Se Valida el precio (puede ser 0, pero no menor que 0)
        price = data.get('price')
        if not isinstance(price, (int, float)) or price < 0:
            response_body['results'] = {}
            response_body['message'] = 'El precio debe ser un número mayor o igual a 0'
            return response_body, 400
        
        # Se validan los puentos (puede ser 0, pero no menor que 0)
        points = data.get('points')
        if not isinstance(points, (int, float)) or points < 0:
            response_body['results'] = {}
            response_body['message'] = 'Los puntos deben ser un número mayor o igual a 0'
            return response_body, 400
        
        row = Courses(title=data.get('title', '').strip(),
                      description=data.get('description', 'info no disponible').strip(),
                      price=price,
                      is_active=data.get('is_active', True),
                      points=points,
                      created_by=user_id)
        
        db.session.add(row)
        db.session.commit()

        response_body['message'] = 'Curso creado exitosamente'
        response_body['results'] = row.serialize()
        
        return response_body, 201
    
    return response_body, 405

@api.route('/courses-private/<int:course_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def course_private(course_id):
    response_body = {}

    # 1. Validar usuario autenticado y obtener datos del JWT con el helper correspondiente
    user, response_body_validation, status = validate_active_user()
    if response_body_validation:
        return response_body_validation, status
    
    user_id = user.get('user_id')
    is_admin = user.get('is_admin', False)
    user_role = user.get('role')

    # 2. Buscar curso por ID
    row = db.session.execute(db.select(Courses).where(Courses.course_id == course_id)).scalar()
    
    if not row:
        response_body['message'] = f'Curso {course_id} no encontrado'
        return response_body, 404

    if request.method == 'GET':
        response_body['message'] = f'Detalles del curso {course_id}'
        response_body['results'] = row.serialize()
        return response_body, 200

    if request.method == 'PUT':
        # Solo admin y el profesor que creó el curso puede actualizar
        if not is_admin:
            if user_role != 'teacher':
                response_body['message'] = 'No eres un Administrado ni profesor, no puedes actualizar cursos'
                return response_body, 403
            # Profesor solo puede actualizar sus propios cursos
            if row.created_by != user_id:
                response_body['message'] = 'No puedes actualizar cursos de otros profesores'
                return response_body, 403

        # Validar JSON
        data, error_response, status = validate_request_json()
        if error_response:
            return error_response, status

        # Validaciones de datos
        if 'price' in data:
            price = data['price']
            if not isinstance(price, (int, float)) or price < 0:
                response_body['message'] = 'El precio debe debe de ser un número mayor o igual a 0'
                return response_body, 400
            row.price = price
        
        if 'points' in data:
            points = data['points']
            if not isinstance(points, (int, float)) or points < 0:
                response_body['message'] = 'Los puntos deben ser un número mayor o igual a 0'
                return response_body, 400
            row.points = points
        
        # Actualizar otros campos
        if 'title' in data:
            row.title = data['title'].strip()
        if 'description' in data:
            row.description = data['description'].strip()
        if 'is_active' in data:
            row.is_active = bool(data['is_active'])

        db.session.commit()
        
        response_body['results'] = row.serialize()
        response_body['message'] = f'Curso {course_id} Actualizado'
        return response_body, 200

    if request.method == 'DELETE':
        # Solo admin y el profesor que creó el curso puede eliminar
        if not is_admin:
            if user_role != 'teacher':
                response_body['message'] = 'No eres un administrador o profesor, no puedes eliminar cursos'
                return response_body, 403
            # Profesor solo puede eliminar sus propios cursos
            if row.created_by != user_id:
                response_body['message'] = 'No puedes eliminar cursos de otros profesores'
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
        # Obtener y validar parámetros
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=20, type=int)
        
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 20
        
        offset = (page - 1) * per_page
        
        # Contar total
        total_query = db.session.execute(
            db.select(db.func.count()).select_from(Modules)
        ).scalar()
        
        # Obtener con paginación
        rows = db.session.execute(
            db.select(Modules)
            .order_by(Modules.module_id)
            .limit(per_page)
            .offset(offset)
        ).scalars()
        
        results = [row.serialize() for row in rows]
        
        # Calcular páginas totales
        total_pages = 0
        if per_page > 0 and total_query:
            total_pages = (total_query + per_page - 1) // per_page
        
        response_body['results'] = results
        response_body['message'] = 'Listado de módulos'
        response_body['count'] = len(results)
        response_body['pagination'] = {
            'page': page,
            'per_page': per_page,
            'total': total_query,
            'total_pages': total_pages
        }
        return response_body, 200
    
    return response_body, 405

@api.route('/modules-private', methods=['GET', 'POST'])
@jwt_required()
def modules_private():
    response_body = {}

    # 1. Validar usuario autenticado y obtener datos del JWT con el helper correspondiente
    user, response_body_validation, status = validate_active_user()
    if response_body_validation:
        return response_body_validation, status
    
    user_id = user.get('user_id')
    is_admin = user.get('is_admin', False)
    user_role = user.get('role')

    if request.method == 'GET':
        # Obtener parámetros de paginación
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=20, type=int)
        
        # Validar parámetros
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 20
        
        offset = (page - 1) * per_page
        
        # Contar total
        total_query = db.session.execute(db.select(db.func.count()).select_from(Modules)).scalar()
        
        # Obtener módulos con paginación
        rows = db.session.execute(db.select(Modules).order_by(Modules.module_id).limit(per_page).offset(offset)).scalars()
        
        results = [row.serialize() for row in rows]
        
        # Calcular páginas totales
        total_pages = 0
        if per_page > 0 and total_query:
            total_pages = (total_query + per_page - 1) // per_page
        
        response_body['message'] = 'Listado de módulos'
        response_body['count'] = len(results)
        response_body['results'] = results
        response_body['pagination'] = {
            'page': page,
            'per_page': per_page,
            'total': total_query,
            'total_pages': total_pages
        }
        return response_body, 200

    if request.method == 'POST':
        # Solo admin y profesor pueden crear módulos
        if not is_admin and user_role != 'teacher':
            response_body['message'] = 'No autorizado para crear módulos, no es Administrador ni profesor'
            return response_body, 403
        
        # Validar JSON y campos requeridos 
        data, error_response, status = validate_request_json(['title', 'order', 'points', 'course_id'])
        if error_response:
            return error_response, status
        
        course_id = data.get('course_id')
        
        # Verificar que el curso exista 
        course = db.session.execute(db.select(Courses).where(Courses.course_id == course_id)).scalar()
        if not course:
            response_body['message'] = 'Curso no encontrado'
            return response_body, 400

        points = data.get('points')
        if not isinstance(points, (int, float)) or points < 0:
            response_body['message'] = 'Los puntos deben ser un número mayor o igual a 0'
            return response_body, 400
        
        # Se vereifica el orden del módulo dentro del curso 
        existing_module = db.session.execute(
            db.select(Modules).where(Modules.course_id == course_id, Modules.order == data.get('order'))).scalar()
        
        if existing_module:
            response_body['message'] = f'Ya existe un módulo con el orden {data.get("order")} en este curso'
            return response_body, 409
        
        row = Modules(title=data.get('title', '').strip(),
                      order=data.get('order'),
                      points=points,
                      course_id=course_id)
        
        db.session.add(row)
        db.session.commit()

        response_body['message'] = 'Módulo creado exitosamente'
        response_body['results'] = row.serialize()
        
        return response_body, 201
    
    return response_body, 405

@api.route('/modules/<int:module_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def module_private(module_id):
    response_body = {}
    
    # se valida usuario autenticado y obtener datos del JWT con el helper correspondiente
    user, response_body_validation, status = validate_active_user()
    if response_body_validation:
        return response_body_validation, status
       
    row = db.session.execute(db.select(Modules).where(Modules.module_id == module_id)).scalar()
    
    # Se verifica si existe
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
                response_body['message'] = 'Solo el administrador y profesor pueden actualizar módulos'
                return response_body, 403
        
        # Solo el profesor que creó el curso al que pertenece el módulo puede actualizarlo
        if user.get('role') == 'teacher' and not user.get('is_admin'):
            
            # Verificar que el módulo pertenezca a un curso del profesor
            course_owner = db.session.execute(db.select(Courses).where(Courses.course_id == row.course_id,Courses.created_by == user.get('user_id'))).scalar()
            if not course_owner:
                response_body['message'] = 'No tienes permiso para modificar módulos de este curso'
                return response_body, 403

        data = request.json
        # se valida que las claves requeridas estén en el request body
        if not data:
            response_body['message'] = 'Request body requerido para actualizar'
            return response_body, 400

        # se verifica si se está actualizando
        if 'course_id' in data:
            course = db.session.execute(db.select(Courses).where(Courses.course_id == data.get('course_id'))).scalar()
            if not course:
                response_body['message'] = 'Curso no encontrado'
                return response_body, 400
        
        # se verifica si se está actualizando el order
        target_course_id = data.get('course_id', row.course_id)

        if 'order' in data:
            existing_module = db.session.execute(db.select(Modules).where(Modules.course_id == target_course_id,
                                                                          Modules.order == data.get('order'),
                                                                          Modules.module_id != module_id)).scalar()
            if existing_module:
                response_body['message'] = f'Ya existe un módulo con el orden {data.get("order")} en este curso'
                return response_body, 409
        
        if 'points' in data:
            points = data['points']
            if not isinstance(points, (int, float)) or points < 0:
                response_body['message'] = 'Los puntos deben ser un número mayor o igual a 0'
                return response_body, 400
            row.points = points
        
        # Actualizar campos
        if 'title' in data:
            row.title = data.get('title', row.title)
        if 'order' in data:
            row.order = data.get('order', row.order)
        if 'course_id' in data:
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
        
        # Solo el profesor que creó el curso al que pertenece el módulo puede eliminarlo
        if user.get('role') == 'teacher' and not user.get('is_admin'):
            course_owner = db.session.execute(db.select(Courses)
                                              .where(Courses.course_id == row.course_id,Courses.created_by == user.get('user_id'))).scalar()
            if not course_owner:
                response_body['message'] = 'No tienes permiso para eliminar módulos de este curso'
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
        required_fields = ['title', 'content', 'learning_objective',
            'signs_taught', 'order', 'trial_version', 'module_id']
        missing_fields = [
            field for field in required_fields if field not in data]
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
                      module_id=data.get('module_id'),
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

    # Se busca el curso por ID
    row = db.session.execute(
        db.select(Lessons).where(Lessons.lesson_id == lesson_id)).scalar()
    # Se verifica si existe
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

        # se verifica si se está actualizando el module_id
        if 'module_id' in data and data.get('module_id') != row.module_id:
            module = db.session.execute(db.select(Modules).where
                                        (Modules.id == data.get('module_id'))).scalar()
        if not module:
            response_body['message'] = 'Módulo no encontrado'
            return response_body, 400

        row.title = data.get('title', row.title)
        row.content = data.get('content', row.content)
        row.learning_objective = data.get(
            'learning_objective', row.learning_objective)
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


@api.route('/purchases-public', methods=['POST'])
def purchases_public():
    response_body = {}

    # Validar datos recibidos
    data = request.json
    if not data:
        response_body['message'] = 'Request body requerido'
        return response_body, 400
    
    # Verificar que se envíe el curso
    if 'course_id' not in data:
        response_body['message'] = 'Se requiere el ID del curso (course_id)'
        return response_body, 400
    
    # Validar que el curso exista y esté activo
    course = db.session.execute(db.select(Courses).where(
        Courses.course_id == data.get('course_id'),
        Courses.is_active == True)).scalar()
    
    if not course:
        response_body['message'] = 'Curso no encontrado o inactivo'
        return response_body, 404
    
    # Respuesta: necesita registrarse
    response_body['message'] = 'Para realizar compras, debe registrarse como usuario'
    response_body['action_required'] = 'registration'
    response_body['registration_url'] = '/api/register' 
    response_body['course_id'] = data['course_id']
    
    return response_body, 200                                                                                                                                                                                                                                                                                                                                               

@api.route('/purchases-private', methods=['GET', 'POST'])
@jwt_required()
def purchases_private():
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
        # Valida si hay resultados o no 
        if not results:
            response_body['message'] = 'No hay compras registradas aún'
        else:
            response_body['message'] = 'Listado de compras'      
        return response_body, 200

    if request.method == 'POST':
        # Cualquier usuario activo puede crear una compra para activar un curso o ampliar su suscripción
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
        # Se valida que el status sea válido
        if 'status' in data:
            valid_statuses = ['pending', 'completed', 'canceled']
            if data.get('status') not in valid_statuses:
                response_body['message'] = f'Status inválido. Valores permitidos: {valid_statuses}'
                return response_body, 400

        # Se verifica que el curso exista o esté activo
        course = db.session.execute(db.select(Courses).where(
            Courses.course_id == data.get('course_id'),
            Courses.is_active == True)).scalar()
        if not course:
            response_body['message'] = 'Curso no encontrado'
            return response_body, 400
        # Validar que el usuario exista
        user_exists = db.session.execute(db.select(Users).where(Users.user_id == data.get('user_id'))).scalar()
        # Validar que el usuario solo pueda crear compras para sí mismo
        jwt_user_id = user.get('user_id')
        request_user_id = data.get('user_id')
        if not user_exists:
            response_body['message'] = 'Usuario no encontrado'
            return response_body, 400
        
        if not jwt_user_id:
            response_body['message'] = 'Token inválido'
            return response_body, 400

        if str(jwt_user_id) != str(request_user_id):
            response_body['message'] = 'No puede crear compras para otros usuarios'
            return response_body, 403  
        
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
@jwt_required()
def purchase(purchase_id):
    response_body = {}

    # validacion de rol de usuario
    user = get_jwt()

    if not user.get('is_active'):
        response_body['message'] = 'Usuario no autorizado'
        return response_body, 403
    
    row = db.session.execute(
        db.select(Purchases).where(Purchases.purchase_id == purchase_id)).scalar()

    #Se verifica si existe
    if not row:
        response_body['message'] = f'Compra {purchase_id} no encontrada'
        return response_body, 404
    
    if request.method == 'GET':
        # Solo admin puede ver cualquier compra
        if not user.get('is_admin'):
            # solo el usuario dueño de la compra puede verla
            jwt_user_id = user.get('user_id')
            if str(jwt_user_id) != str(row.user_id):
                response_body['message'] = 'No autorizado para ver esta compra'
                return response_body, 403
        response_body['results'] = row.serialize()
        response_body['message'] = f'Detalles de la compra {purchase_id}'
        return response_body, 200
    
    if request.method == 'PUT':
        if not user.get('is_admin'):
            response_body['message'] = 'Solo administradores pueden modificar compras'
            return response_body, 403
        
        data = request.json
        # se valida que las claves requeridas estén en el request body
        if not data:
            response_body['message'] = 'Request body requerido para actualizar'
            return response_body, 400
        
        campos_inmutables = ['price', 'total', 'course_id', 'purchase_date', 'created_by']
        for campo in campos_inmutables:
            if campo in data:
                response_body['message'] = f'El campo {campo} no puede ser modificado'
                return response_body, 400
        
        if 'status' in data:
            valid_statuses = ['pending', 'completed', 'canceled']
            if data.get('status') not in valid_statuses:
                response_body['message'] = f'Status inválido. Valores permitidos: {valid_statuses}'
                return response_body, 400
        
        if 'user_id' in data:
            # Validar que el nuevo usuario exista
            new_user = db.session.execute(db.select(Users).where(Users.user_id == data['user_id'])).scalar()
            if not new_user:
                response_body['message'] = 'Usuario no encontrado'
                return response_body, 400
            row.user_id = data.get('user_id')

        row.status = data.get('status', row.status)
        row.start_date = data.get('start_date', row.start_date)

        db.session.commit()
        response_body['results'] = row.serialize()
        response_body['message'] = f'Compra {purchase_id} actualizada'
        return response_body, 200
    return response_body, 405

@api.route('/my-points', methods=['GET'])
@jwt_required()
def my_points():
    response_body = {}

    # Se valida que el usuario esté activo
    user = get_jwt()
    if not user.get('is_active'):
        response_body['message'] = 'Usuario no autorizado'
        return response_body, 403

    # Se obtiene el user_id del token JWT
    jwt_user_id = user.get('user_id')
    if not jwt_user_id:
        response_body['message'] = 'User ID no encontrado en token'
        return response_body, 400

    # Se obtienen los puntos del usuario ordenados por fecha (más recientes primero)
    points_rows = db.session.execute(db.select(UserPoints)
                                     .where(UserPoints.user_id == jwt_user_id)
                                     .order_by(UserPoints.date.desc())).scalars()

    # Se serializan los puntos para la respuesta
    points_details = [row.serialize() for row in points_rows]

    # Se calcula el total de puntos sumando los puntos del usuario
    total_points = db.session.execute(db.select(func.sum(UserPoints.points))
                                      .where(UserPoints.user_id == jwt_user_id)).scalar() or 0

    # Se obtiene la información básica del usuario
    user_info = db.session.execute(db.select(Users).where(Users.user_id == jwt_user_id)).scalar()

    response_body['message'] = 'Resumen de puntos del usuario'
    response_body['results'] = {
        'user_id': jwt_user_id,
        'total_points': float(total_points) if total_points else 0,
        'points_details': points_details,
        'points_count': len(points_details),
        'user_info': {
            'full_name': getattr(user_info, 'full_name', ''),
            'email': getattr(user_info, 'email', '')
        } if user_info else {}
    }
    
    return response_body, 200



@api.route('/user-points', methods=['GET', 'POST'])
@jwt_required()
def user_points():
    response_body = {}

    # validacion de rol de usuario
    user = get_jwt()
    if not user.get('is_active'):
        response_body['message'] = 'Usuario no autorizado'
        return response_body, 403
    
    if request.method == 'GET':
        # Se suma los puntos por usuario y se ordena de mayor a menor
        points_query = db.session.execute(db.select(UserPoints.user_id,
                                          func.sum(UserPoints.points).label('total_points'))
                                          .group_by(UserPoints.user_id)
                                          .order_by(func.sum(UserPoints.points).desc())).all()

        # Se obtienen los detalles de los usuarios en la lista de puntos
        user_ids = [user_id for user_id, _ in points_query]
        users = db.session.execute(db.select(Users)
                                   .where(Users.user_id.in_(user_ids))).scalars()

        # Se serializan los usuarios en un diccionario para acceso rápido
        serialized_users = {user.user_id: user.serialize() for user in users}

        # Se procesan los resultados
        results = []
        for rank, (user_id, total_points) in enumerate(points_query, 1):
            user_data = serialized_users.get(user_id, {})
            user_data['rank'] = rank
            user_data['total_points'] = float(total_points) if total_points else 0
            results.append(user_data)
        
        response_body['message'] = 'User points list'
        response_body['results'] = results
        return response_body, 200
    

    if request.method == 'POST':
        # Solo admin y profesor pueden colocar puntos
        if not user.get('is_admin'):
            if user.get('role') != 'teacher':
                response_body['message'] = 'No autorizado para crear puntos de usuario, no es admin ni teacher'
                return response_body, 403
            
        data = request.json
        
        # Se Valida que el request body no esté vacío
        if not data:
            response_body['message'] = 'Request body requerido'
            return response_body, 400
        
        # Se valida que las claves requeridas estén en el request body
        required_fields = ['user_id', 'points']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            response_body['message'] = 'Faltan campos requeridos'
            response_body['missing_fields'] = missing_fields
            return response_body, 400
        
        # Se  valida que el usuario exista
        user_exists = db.session.execute(
            db.select(Users).where(Users.user_id == data.get('user_id'))).scalar()
        
        if not user_exists:
            response_body['message'] = 'Usuario no encontrado'
            return response_body, 400
        
        row = UserPoints(
            user_id=data.get('user_id'),
            points=data.get('points'),
            type=data.get('type', 'course'),
            event_description=data.get('event_description'),
            date=data.get('date'))
        db.session.add(row)
        db.session.commit()
        response_body['message'] = 'Puntos de usuario creados'
        response_body['results'] = row.serialize()
        return response_body, 201
    return response_body, 405



@api.route('/user-points/<int:point_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def user_point(point_id):
    response_body = {}

    # validacion de rol de usuario
    user = get_jwt()
    if not user.get('is_active'):
        response_body['message'] = 'Usuario no autorizado'
        return response_body, 403

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
        # Solo admin y profesor pueden actualizar puntos
        if not user.get('is_admin'):
            if user.get('role') != 'teacher':
                response_body['message'] = 'No eres un Admin ni Teacher, no puedes actualizar puntos'
                return response_body, 403

        # se valida que las claves requeridas estén en el request body
        data = request.json

        if not data:
            response_body['message'] = 'Request body requerido para actualizar'
            return response_body, 400

        # Validar que user_id exista si se está actualizando
        if 'user_id' in data:
            user_exists = db.session.execute(
                db.select(Users).where(Users.user_id == data['user_id'])
            ).scalar()
            if not user_exists:
                response_body['message'] = 'Usuario no encontrado'
                return response_body, 400
            
        row.points = data.get('points', row.points)
        row.type = data.get('type', row.type)
        row.event_description = data.get(
            'event_description', row.event_description)
        row.date = data.get('date', row.date)
        row.user_id = data.get('user_id', row.user_id)
        db.session.commit()
        response_body['results'] = row.serialize()
        response_body['message'] = f'Punto {point_id} actualizado'
        return response_body, 200
    
    if request.method == 'DELETE':
        # Solo admin y profesor pueden eliminar puntos
        if not user.get('is_admin'):
            if user.get('role') != 'teacher':
                response_body['message'] = 'No eres un Admin ni Teacher, no puedes eliminar puntos'
                return response_body, 403
        db.session.delete(row)
        db.session.commit()
        response_body['message'] = f'Punto {point_id} eliminado'
        return response_body, 200
    return response_body, 405



@api.route('/userprogress', methods=['GET', 'POST', 'DELETE'])
@jwt_required()
def userprogress():
    #Usuario activo
    response_body = {}
    user = get_jwt()
    if not user.get('is_active'):
        response_body['message'] = 'Usuario no autorizado'
        return response_body, 403

    current_user_id = user.get('user_id')
    role = user.get('role')
    is_admin = user.get('is_admin')
#Método GET
    if request.method == 'GET':
        if is_admin or role == 'teacher':
            rows = db.session.execute(db.select(UserProgress)).scalars().all()
            #response_body['results'] = [start_date(r.serialize()) for r in rows]
            response_body['message'] = 'Listado general de progreso de todos los usuarios'
            return response_body, 200
        rows = db.session.execute(db.select(UserProgress).where(UserProgress.user_id == current_user_id)).scalars().all()
        #verificar que row es mayor a 0 o = a 0. Si es = 0 se devuelve mensaje que no tiene curso contratado. 

        progress =[1 for r in rows if r.completed]
        
        #reponse_boy en el results hay que dar la el % que es lo acumulado sobre los progresos del curso

        response_body['results'] = progress.count(1)/len(rows) 
        response_body['message'] = f'Listado de progreso del usuario {current_user_id}'
        return response_body, 200
#Método Post 
    if request.method == 'POST':
        data = request.json
        if not data:
            response_body['message'] = 'Request body requerido'
            return response_body, 400
        required_fields = ['lesson_id', 'user_id', 'completed', 'start_date']
        missing_fields = [f for f in required_fields if f not in data]
        if missing_fields:
            response_body['message'] = 'Faltan campos requeridos'
            response_body['missing_fields'] = missing_fields
            return response_body, 400
        target_user_id = data.get('user_id')
        if not is_admin and role != 'teacher' and target_user_id != current_user_id:
            response_body['message'] = 'No autorizado para crear progreso de otro usuario'
            return response_body, 403
        if not isinstance(data.get('completed'), bool):
            response_body['message'] = 'completed debe ser boolean (true/false)'
            return response_body, 400
        existing = db.session.execute(db.select(UserProgress).where(UserProgress.user_id == target_user_id, UserProgress.lesson_id == data.get('lesson_id'))).scalar()
        if existing:
            response_body['message'] = 'Ya existe un progreso para este usuario en esta lección'
            response_body['results'] = fix_datetime(existing.serialize())
            return response_body, 400
        row = UserProgress(user_id=target_user_id, lesson_id=data.get('lesson_id'), completed=data.get('completed'), start_date=data.get('start_date'), completion_date=data.get('completion_date'))
        db.session.add(row)
        db.session.commit()
        response_body['results'] = fix_datetime(row.serialize())
        response_body['message'] = 'Progreso creado'
        return response_body, 201

    if request.method == 'DELETE':
        if not is_admin and role != 'teacher':
            response_body['message'] = 'No autorizado para eliminar progreso'
            return response_body, 403
        data = request.json
        if not data:
            response_body['message'] = 'Request body requerido para eliminar progreso'
            return response_body, 400
        required_fields = ['user_id', 'lesson_id']
        missing_fields = [f for f in required_fields if f not in data]
        if missing_fields:
            response_body['message'] = 'Faltan campos requeridos'
            response_body['missing_fields'] = missing_fields
            return response_body, 400
        row = db.session.execute(db.select(UserProgress).where(UserProgress.user_id == data.get('user_id'), UserProgress.lesson_id == data.get('lesson_id'))).scalar()
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

    if not user.get('is_active'):
        response_body['message'] = 'Usuario no autorizado'
        return response_body, 403

    current_user_id = user.get('user_id')
    role = user.get('role')
    is_admin = user.get('is_admin')

    row = db.session.execute(
        db.select(UserProgress).where(
            UserProgress.lesson_id == lesson_id,
            UserProgress.user_id == current_user_id )).scalar()

    if not row:
        response_body['message'] = 'Progreso de usuario no encontrado'
        return response_body, 404

    #  GET
    if request.method == 'GET':
        response_body['results'] = fix_datetime(row.serialize())
        response_body['message'] = f'Detalles del progreso para lesson_id {lesson_id}'
        return response_body, 200

    # Bloqueo alumnos
    if role == 'alumno' or (not is_admin and role != 'teacher'):
        response_body['message'] = 'Acceso denegado: No tienes permisos para modificar o eliminar progresos'
        return response_body, 403

    #  PUT
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

        response_body['results'] = fix_datetime(row.serialize())
        response_body['message'] = f'Progreso actualizado para lesson_id {lesson_id}'
        return response_body, 200

    # DELETE
    if request.method == 'DELETE':
        db.session.delete(row)
        db.session.commit()
        response_body['message'] = f'Progreso eliminado para lesson_id {lesson_id}'
        return response_body, 200
    return response_body, 404


@api.route('/achievements', methods=['GET', 'POST'])
def achievements():
    response_body = {}

    if request.method == 'GET':
        rows = db.session.execute(
            db.select(Achievements)).scalars()
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
            icon=data.get('icon'))
        db.session.add(row)
        db.session.commit()
        response_body['results'] = row.serialize()
        response_body['message'] = 'Logro creado'
        return response_body, 201
    return response_body, 404


@api.route('/achievements/<int:achievement_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def achievement(achievement_id):
    response_body = {}
    user = get_jwt()

    # Buscar logro por ID
    row = db.session.execute(
        db.select(Achievements).where(Achievements.achievement_id == achievement_id)).scalar()
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

   



@api.route('/user-achievements', methods=['GET', 'POST'])
@jwt_required()
def user_achievements():
    response_body = {}
     # validacion de rol de usuario
    user = get_jwt()

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
        # Validación 2: Rol, Solo admin y profesor pueden crear cursos
        if not user.get('is_admin'):
            if user.get('role') != 'teacher':
                response_body['message'] = 'No autorizado para asignar logros'
                return response_body, 403
        # Validación 3: body requerido, Se valida que el request body no esté vacío
        data = request.json
        if not data:
            response_body['message'] = 'Request body requerido'
            return response_body, 400
        # Validación 4: campos,requeridos, se valida que las claves requeridas estén en el request body
        required_fields = ['user_id', 'achievement_id']
        missing_fields = [
            field for field in required_fields if field not in data]
        if missing_fields:
            response_body['message'] = 'Faltan campos requeridos'
            response_body['missing_fields'] = missing_fields
            return response_body, 400

        # Validación 5: usuario existe
        user_exists = db.session.execute(
            db.select(Users).where(Users.user_id == data.get('user_id'))).scalar()
        if not user_exists:
            response_body['message'] = 'Usuario no encontrado'
            return response_body, 400

        # Validación 6: logro ya existe
        achievement_exists = db.session.execute(
            db.select(Achievements).where(
                Achievements.achievement_id == data.get('achievement_id'))).scalar()
        if not achievement_exists:
            response_body['message'] = 'Logro no encontrado'
            return response_body, 400

        # Validación 7: evitar logros duplicados
        existing = db.session.execute(
            db.select(UserAchievements).where(
                UserAchievements.user_id == data.get('user_id'),
                UserAchievements.achievement_id == data.get('achievement_id'))).scalar()
        if existing:
            response_body['message'] = 'El usuario ya tiene este logro'
            return response_body, 409

        # Validación 8: fecha valida
        obtained_date = datetime.utcnow()
        if data.get('obtained_date'):
            try:
                obtained_date = datetime.fromisoformat(
                    data.get('obtained_date'))
            except ValueError:
                response_body['message'] = 'Formato de fecha inválido'
                return response_body, 400

        # Creación
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
@jwt_required()
def user_achievement(user_achievement_id):
    response_body = {}
    user = get_jwt()

     # Validación 1: usuario activo
    if not user.get('is_active'):
        response_body['message'] = 'Usuario no autorizado'
        return response_body, 403

     # Validación 2: si el logro existe
    row = db.session.execute(
        db.select(UserAchievements).where(
            UserAchievements.user_achievement_id == user_achievement_id)).scalar()
    if not row:
        response_body['message'] = 'Logro de usuario no encontrado'
        return response_body, 404

    if request.method == 'GET':
        if not user.get('is_admin') and user.get('role') != 'teacher':
            if row.user_id != user.get('user_id'):
                response_body['message'] = 'No autorizado para ver este logro'
                return response_body, 403
        response_body['results'] = row.serialize()
        response_body['message'] = f'Detalles del logro de usuario {user_achievement_id}'
        return response_body, 200

    if request.method == 'PUT':
        if not user.get('is_admin') and user.get('role') != 'teacher':
            response_body['message'] = 'No autorizado para actualizar logros'
            return response_body, 403
        data = request.json
        if not data:
             response_body['message'] = 'Request body requerido'
             return response_body, 400

        row.obtained_date = data.get('obtained_date', row.obtained_date)
        db.session.commit()
        response_body['results'] = row.serialize()
        response_body['message'] = f'Logro de usuario {user_achievement_id} actualizado'
        return response_body, 200

    if request.method == 'DELETE':
       if not user.get('is_admin'):
         response_body['message'] = 'Solo admin puede eliminar logros'
         return response_body, 403

    db.session.delete(row)
    db.session.commit()
    response_body['message'] = f'Logro de usuario {user_achievement_id} eliminado'
    return response_body, 200


@api.route('/multimedia-resources', methods=['GET', 'POST'])
@jwt_required()
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

        # Validación 1: en el body
        if not data:
            response_body['message'] = 'Request body requerido'
            return response_body, 400
        
        # Validación 2: campos requeridos
        required_fields = ['type', 'url', 'order', 'lesson_id']
        missing_fields = [f for f in required_fields if f not in data]
        if missing_fields:
            response_body['message'] = 'Faltan campos requeridos'
            response_body['missing_fields'] = missing_fields
            return response_body, 400
        
        # Validación 3: tipo permitido
        allowed_types = ['video', 'image', 'gif', 'animation', 'document']
        if data.get('type') not in allowed_types:
            response_body['message'] = 'Tipo de recurso inválido'
            return response_body, 400
        
        # Validación 4: URL valida
        if not data.get('url').startswith(('http://', 'https://')):
            response_body['message'] = 'URL inválida'
            return response_body, 400
        
        # Validación 5:lección existe
        lesson = db.session.execute(
            db.select(Lessons).where(Lessons.lesson_id == data.get('lesson_id'))).scalar()
        if not lesson:
            response_body['message'] = 'Lección no encontrada'
            return response_body, 400

        # Validación 6: orden único
        existing = db.session.execute(
            db.select(MultimediaResources).where(
                MultimediaResources.lesson_id == data.get('lesson_id'),
                MultimediaResources.order == data.get('order'))).scalar()
        if existing:
            response_body['message'] = 'Ya existe un recurso con este orden'
            return response_body, 409
        row = MultimediaResources(type=data.get('type'),
                                  url=data.get('url'),
                                  duration_seconds=data.get('duration_seconds'),
                                  description=data.get('description'),
                                  order=data.get('order'),
                                  lesson_id=data.get('lesson_id'))
        db.session.add(row)
        db.session.commit()
        response_body['results'] = row.serialize()
        response_body['message'] = 'Recurso multimedia creado'
        return response_body, 201
    return response_body, 405

@api.route('/multimedia-resources/<int:resource_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def multimedia_resource(resource_id):
    response_body = {}
    user = get_jwt()

    # Validación 1: usuario activo
    if not user.get('is_active'):
        response_body['message'] = 'Usuario no autorizado'
        return response_body, 403

    # Validación 2: existe
    row = db.session.execute(
        db.select(MultimediaResources).where(
            MultimediaResources.resource_id == resource_id)).scalar()
    if not row:
        response_body['message'] = 'Recurso multimedia no encontrado'
        return response_body, 404

    if request.method == 'GET':
        response_body['results'] = row.serialize()
        response_body['message'] = 'Detalle del recurso multimedia'
        return response_body, 200

    if request.method == 'PUT':
        if not user.get('is_admin') and user.get('role') != 'teacher':
            response_body['message'] = 'No autorizado para actualizar recursos'
            return response_body, 403

        data = request.json
        if not data:
            response_body['message'] = 'Request body requerido'
            return response_body, 400
        row = db.session.execute(db.select(MultimediaResources).where
        (MultimediaResources.resource_id == resource_id)).scalar()
   
        row.type = data.get('type', row.type)
        row.url = data.get('url', row.url)
        row.order = data.get('order', row.order)
        row.description = data.get('description', row.description)
        row.duration_seconds = data.get('duration_seconds', row.duration_seconds)
        db.session.commit()
        response_body['results'] = row.serialize()
        response_body['message'] = 'Recurso multimedia actualizado'
        return response_body, 200

    if request.method == 'DELETE':
        if not user.get('is_admin'):
            response_body['message'] = 'Solo admin puede eliminar recursos'
            return response_body, 403

        db.session.delete(row)
        db.session.commit()
        response_body['message'] = 'Recurso multimedia eliminado'
        return response_body, 200
   

