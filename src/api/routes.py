"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import uuid
import json
from datetime import datetime, timezone, timedelta

from sqlalchemy import func
from werkzeug.security import (check_password_hash,generate_password_hash)

from flask import Blueprint, request, current_app
from flask_cors import CORS
from flask_jwt_extended import (create_access_token,get_jwt_identity,jwt_required,get_jwt)

from api.models import (db,Users,Courses,Modules,Lessons,MultimediaResources,Purchases,Achievements,UserPoints,UserProgress,UserAchievements)


from .cloudinary_service import cloudinary_service 
import cloudinary.uploader

from .stripe_service import stripe_service

api = Blueprint('api', __name__)
CORS(api)

""" --- HELPERS DE VALIDACIÓN --- """

# Verifica usuario activo con JWT válido
def validate_active_user():
    user = get_jwt()
    
    if not user:
        response_body = {
            'message': 'Token inválido o no proporcionado',
            'results': {}
        }
        return None, response_body, 401
    
    if not user.get('is_active', False):
        response_body = {
            'message': 'Usuario no autorizado',
            'results': {}
        }
        return None, response_body, 403
    
    trial_date_parseable = False
    
    if user.get('role') == 'demo':
        trial_end_date = user.get('trial_end_date')
        
        if trial_end_date and isinstance(trial_end_date, str) and trial_end_date.strip():
            if 'T' in trial_end_date and '-' in trial_end_date:
                try:
                    date_str = trial_end_date.replace('Z', '+00:00')
                    trial_end = datetime.fromisoformat(date_str)
                    trial_date_parseable = True
                    
                    now = datetime.now(timezone.utc)
                    if trial_end < now:
                        response_body = {
                            'message': 'Periodo de trial expirado. Por favor, actualice su plan.',
                            'results': {}
                        }
                        return None, response_body, 403
                        
                except ValueError:
                    print(f"⚠️ ADVERTENCIA: Formato trial_end_date inválido para usuario {user.get('user_id')}: {trial_end_date}")
                    
    user['_trial_date_parseable'] = trial_date_parseable
    
    return user, None, 200

# Valida roles de usuario y permisos
def validate_user_role(
    require_role=None,
    allowed_roles=None,
    require_admin=False,
    allow_demo=False
):
    user, response_body, status_code = validate_active_user()
    if response_body:
        return None, response_body, status_code
    
    user_role = user.get('role')
    is_admin = user.get('is_admin', False)
    
    if require_admin:
        if not is_admin:
            response_body = {
                'message': 'Se requieren permisos de administrador',
                'results': {}
            }
            return None, response_body, 403
        return user, None, 200
    
    if is_admin:
        return user, None, 200
    
    if user_role == 'demo' and not allow_demo:
        response_body = {
            'message': 'Usuarios demo tienen acceso limitado',
            'results': {}
        }
        return None, response_body, 403
    
    if require_role is not None:
        if user_role != require_role:
            response_body = {
                'message': f'Se requiere rol de {require_role}',
                'results': {}
            }
            return None, response_body, 403
        return user, None, 200
    
    if allowed_roles is not None:
        if user_role not in allowed_roles:
            if len(allowed_roles) == 1:
                msg = f'Se requiere rol de {allowed_roles[0]}'
            else:
                msg = f'Se requiere uno de estos roles: {", ".join(allowed_roles)}'
            
            response_body = {
                'message': msg,
                'results': {}
            }
            return None, response_body, 403
        return user, None, 200
    
    return user, None, 200

# Valida que el request tenga JSON y campos requeridos
def validate_request_json(required_fields=None):
    if not request.json: 
        response_body = {
            'message': 'Request body requerido. Envía los datos en formato JSON.',
            'results': {}
        }
        return None, response_body, 400
    
    received_data = request.json 
    
    if required_fields:
        missing_fields = []
        
        for field in required_fields:
            if field not in received_data:
                missing_fields.append(field)
        
        if missing_fields:
            response_body = {
                'message': 'Faltan campos requeridos en los datos',
                'results': {},
                'missing_fields': missing_fields 
            }
            return None, response_body, 400
    
    return received_data, None, 200

# Valida datos y campos requeridos
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

# Obtiene información del trial para usuarios demo
def get_trial_info(user):
    if user.get('role') != 'demo':
        return None
    
    trial_end_date = user.get('trial_end_date')
    
    if not trial_end_date or not isinstance(trial_end_date, str):
        return None
    
    if not trial_end_date.strip():
        return None
    
    if not user.get('_trial_date_parseable', False):
        return None
    
    date_str = trial_end_date.replace('Z', '+00:00')
    trial_end = datetime.fromisoformat(date_str)
    now = datetime.now(timezone.utc)
    
    days_left = (trial_end - now).days
    
    return {
        'trial_end_date': trial_end_date,
        'days_remaining': max(days_left, 0),
        'status': 'active' if days_left > 0 else 'expired'
    }

# Crea lección con datos JSON
def _handle_json_create(request, user_id, user):
    data, error_response, status = validate_request_json([
        'title', 'content', 'module_id', 'order', 'trial_visible'
    ])
    if error_response:
        return error_response, status
    
    # Validar contenido no vacío
    content = data.get('content', '').strip()
    if not content:
        return {
            'message': 'El contenido de la lección no puede estar vacío',
            'results': {}
        }, 400
    
    # Validar orden
    if not isinstance(data.get('order'), int) or data['order'] < 0:
        return {
            'message': 'El orden debe ser un número entero no negativo',
            'results': {}
        }, 400
    
    # Validar trial_visible
    if not isinstance(data.get('trial_visible'), bool):
        return {
            'message': 'trial_visible debe ser true o false',
            'results': {}
        }, 400
    
    # Validar que el módulo existe
    module_exists = db.session.execute(
        db.select(Modules).where(Modules.module_id == data['module_id'])
    ).scalar()
    
    if not module_exists:
        return {
            'message': 'El módulo especificado no existe',
            'results': {}
        }, 400
    
    # Validar título no vacío
    title = data.get('title', '').strip()
    if not title:
        return {
            'message': 'El título de la lección no puede estar vacío',
            'results': {}
        }, 400
    
    # Crear lección
    row = Lessons(
        title=title,
        content=content,
        learning_objective=data.get('learning_objective', '').strip(),
        signs_taught=data.get('signs_taught', '').strip(),
        order=data['order'],
        trial_visible=data['trial_visible'],
        module_id=data['module_id'],
        is_active=True
    )
    
    db.session.add(row)
    db.session.commit()

    return {
        'message': 'Lección creada exitosamente',
        'results': row.serialize()
    }, 201

# Crea lección con archivos multimedia
def _handle_multipart_upload(request, user_id, user):
    title = request.form.get("title")
    content = request.form.get("content")
    module_id = request.form.get("module_id", type=int)
    order = request.form.get("order", type=int)
    trial_visible = request.form.get("trial_visible", "false").lower() == "true"

    if not all([title, content, module_id, order]):
        return {
            "message": "Faltan campos obligatorios",
            "results": {}
        }, 400

    lesson = Lessons(
        title=title,
        content=content,
        module_id=module_id,
        order=order,
        trial_visible=trial_visible
    )

    db.session.add(lesson)
    db.session.flush()

    module = db.session.get(Modules, module_id)
    course_id = module.course_id

    files = request.files.getlist("files")
    descriptions = request.form.getlist("descriptions")

    multimedia_list = []

    for index, file in enumerate(files, start=1):
        filename = file.filename.lower()

        if filename.endswith((".jpg", ".jpeg", ".png")):
            media_type = "image"
            cloudinary_type = "image"
            folder_type = "images"

        elif filename.endswith(".gif"):
            media_type = "gif"
            cloudinary_type = "video"
            folder_type = "gifs"

        elif filename.endswith((".mp4", ".mov", ".avi")):
            media_type = "video"
            cloudinary_type = "video"
            folder_type = "videos"

        elif filename.endswith((".pdf", ".docx", ".xlsx")):
            media_type = "document"
            cloudinary_type = "raw"
            folder_type = "documents"

        else:
            continue

        folder = (
            f"courses/course_{course_id}/"
            f"module_{module_id}/"
            f"lesson_{lesson.lesson_id}/"
            f"{folder_type}"
        )

        result = cloudinary.uploader.upload(
            file,
            resource_type=cloudinary_type,
            folder=folder,
            public_id=f"resource_{index}",
            overwrite=True
        )

        media = MultimediaResources(
            lesson_id=lesson.lesson_id,
            resource_type=media_type,
            url=result["secure_url"],
            duration_seconds=result.get("duration"),
            description=descriptions[index - 1] if index - 1 < len(descriptions) else None,
            order=index
        )

        db.session.add(media)
        multimedia_list.append(media)

    db.session.commit()

    return {
        "message": "Lección creada con multimedia",
        "results": {
            "lesson": lesson.serialize(),
            "multimedia": [m.serialize() for m in multimedia_list]
        }
    }, 201

""" --- HELPERS PARA PAGINACIÓN Y RESPUESTAS --- """

# Toma los números de página del URL como ?page=2&per_page=10
def build_pagination_params(request):
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=20, type=int)
    
    if page < 1:
        page = 1
    
    if per_page < 1:
        per_page = 20
    elif per_page > 100:
        per_page = 100
    
    offset = (page - 1) * per_page
    
    return page, per_page, offset

# Crea la respuesta con paginación lista para enviar al cliente 
def build_pagination_response(results, total_count, page, per_page, message=""):
    # Calcular total de páginas
    total_pages = 0
    # calcula el total de páginas solo si per_page es mayor que 0 para evitar división por cero
    if per_page > 0 and total_count:
        # El cálculo de total_pages se hace de esta manera para redondear hacia arriba
        total_pages = (total_count + per_page - 1) // per_page
    
    response_body = {
        'results': results,
        'message': message if message else f'Listado ({len(results)} items)',
        'count': len(results),
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total_count,
            'total_pages': total_pages
        }
    }
    
    return response_body, 200

# Respuesta para métodos no permitidos
def method_not_allowed_response():
    response_body = {
        'message': 'Método no permitido',
        'results': {}
    }
    return response_body, 405

# Respuesta simple cuando todo sale bien
def simple_success_response(data, message=""):
    response_body = {
        'message': message if message else 'Operación exitosa',
        'results': data
    }
    return response_body, 200

# Respuesta cuando hay un error
def simple_error_response(message, status_code=400):
    response_body = {
        'message': message,
        'results': {}
    }
    return response_body, status_code

""" --- RUTAS --- """

# POST: Login de usuario
@api.route("/login", methods=["POST"])
def login():

    # HELPER: validate_request_json - Validar email y password
    data, response_body, status = validate_request_json(["email", "password"])
    if response_body:
        return response_body, status 
    
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    
    if not password:
        return {
            'message': "El usuario debe proporcionar una contraseña",
            'results': {}
        }, 400
    
    row = db.session.execute(db.select(Users).where(Users.email == email,Users.is_active == True)).scalar()
    
    if not row or not check_password_hash(row.password_hash, password):
        return {
            'message': "Correo o contraseña incorrectos, o usuario inactivo",
            'results': {}
        }, 401
    
    user_data = {
        'user_id': row.user_id,
        'is_active': row.is_active,
        'role': row.role,
        'is_admin': row.is_admin,
        'trial_end_date': row.trial_end_date.isoformat() if row.trial_end_date else None 
    }
    
    return {
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
    }, 200

# GET: Ruta protegida para verificar token
@api.route("/protected", methods=["GET"])
@jwt_required()
def protected():

    # HELPER: validate_user_role - Verificar usuario autenticado
    user, response_body, status_code = validate_user_role()
    if response_body:
        return response_body, status_code
    
    response_data = {
        'user_id': user.get('user_id'),
        'email': user.get('email', ''),
        'role': user.get('role'),
        'is_active': user.get('is_active', False),
        'is_admin': user.get('is_admin', False)
    }
    
    # HELPER: get_trial_info - Obtener info de trial si es demo
    trial_info = get_trial_info(user)
    
    response_body = {
        'message': 'Acceso autorizado a información protegida',
        'results': response_data
    }
    
    if trial_info:
        response_body['trial_info'] = trial_info
        
        if user.get('role') == 'demo':
            response_body['trial_limits'] = {
                'max_courses': 1,
                'max_modules_per_course': 1,
                'max_lessons_per_module': 8,
                'remaining_lessons': 'Hasta 8',
                'message': 'Puedes acceder a 1 curso, 1 módulo y máximo 8 lecciones durante tu trial.'
            }
    
    return response_body, 200

# POST: Registrar nuevo usuario demo
@api.route('/register', methods=['POST'])
def register():

    # HELPER: validate_request_json - Validar datos de registro
    data, error_response, status = validate_request_json([
        'email', 'password', 'first_name', 'last_name'
    ])
    if error_response:
        return error_response, status
    
    email = data.get('email', '').strip().lower()
    if '@' not in email or '.' not in email.split('@')[-1]:
        return {
            'message': 'Formato de email inválido',
            'results': {}
        }, 400
    
    password = data.get('password', '')
    if not password:
        return {
            'message': 'La contraseña no puede estar vacía',
            'results': {}
        }, 400
    
    if len(password) < 8:
        return {
            'message': 'La contraseña debe tener al menos 8 caracteres',
            'results': {}
        }, 400
    
    existing_user = db.session.execute(db.select(Users).where(Users.email == email)).scalar()
    
    if existing_user:
        return {
            'message': f'El usuario con email {email} ya existe',
            'results': {}
        }, 409
    
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
    
    return {
        'message': 'Usuario demo creado exitosamente. Trial de 7 días activado.',
        'results': {
            'user_id': row.user_id,
            'email': row.email,
            'first_name': row.first_name,
            'last_name': row.last_name,
            'role': row.role,
            'trial_end_date': trial_end_date.isoformat()
        },
        'trial_info': {
            'duration_days': 7,
            'start_date': now.isoformat(),
            'end_date': trial_end_date.isoformat(),
            'limits': {
                'courses': 1,
                'modules_per_course': 1,
                'lessons_per_module': 8
            }
        }
    }, 201
                                                                                                                                                        
# GET: Listar usuarios (admin ve todos, teacher ve sus estudiantes)
@api.route('/users', methods=['GET'])
@jwt_required()
def get_users():

    # HELPER: validate_user_role - Verificar usuario autenticado
    user, response_body_validation, status = validate_user_role()
    if response_body_validation:
        return response_body_validation, status
    
    user_role = user.get('role')
    is_admin = user.get('is_admin', False)
    teacher_id = user.get('user_id')
    
    # HELPER: build_pagination_params - Obtener parámetros de paginación
    page, per_page, offset = build_pagination_params(request)
    
    if is_admin:
        total_query = db.session.execute(db.select(db.func.count()).select_from(Users)).scalar()
        
        rows = db.session.execute(db.select(Users).order_by(Users.user_id).limit(per_page).offset(offset)).scalars()
        
        results = [row.serialize() for row in rows]
        
        # HELPER: build_pagination_response - Enviar respuesta paginada
        return build_pagination_response(
            results=results,
            total_count=total_query,
            page=page,
            per_page=per_page,
            message='Listado completo de usuarios (vista admin)'
        )
    
    elif user_role == 'teacher':
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
        
        total_count_query = db.session.execute(
            db.select(db.func.count()).select_from(Users)
            .join(Purchases, Users.user_id == Purchases.user_id)
            .join(Courses, Purchases.course_id == Courses.course_id)
            .where(Courses.created_by == teacher_id, Users.role == 'student')
            .distinct()
        ).scalar()
        
        students = list(students_query)
        
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
        
        # HELPER: simple_success_response - Enviar respuesta simple
        return simple_success_response(
            results,
            f'Estudiantes en tus cursos ({len(results)} estudiantes)'
        )
    
    else:
        # HELPER: simple_error_response - Error de permisos
        return simple_error_response('No autorizado para ver listado de usuarios', 403)

# GET/PUT/DELETE: Operaciones CRUD para usuario específico
@api.route('/users/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def user(user_id):
    current_user, error_response, status = validate_user_role()
    if error_response:
        return error_response, status
    
    current_user_id = current_user.get('user_id')
    is_admin = current_user.get('is_admin', False)
    user_role = current_user.get('role')
    
    target_user = db.session.execute(
        db.select(Users).where(Users.user_id == user_id)
    ).scalar()
    
    if not target_user:
        # HELPER: simple_error_response - Usuario no encontrado
        return simple_error_response(f'Usuario {user_id} no encontrado', 404)
    
    if request.method == 'GET':
        if is_admin:
            user_data = target_user.serialize()
        
        elif user_role == 'teacher':
            if current_user_id == user_id:
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
            else:
                is_teacher_student = db.session.execute(
                    db.select(Purchases)
                    .join(Courses, Purchases.course_id == Courses.course_id)
                    .where(
                        Purchases.user_id == user_id,
                        Courses.created_by == current_user_id,
                        target_user.role == 'student'
                    )
                ).scalar()
                
                if is_teacher_student:
                    user_data = {
                        'user_id': target_user.user_id,
                        'first_name': target_user.first_name,
                        'last_name': target_user.last_name,
                        'email': target_user.email,
                        'role': target_user.role,
                        'current_points': target_user.current_points,
                        'is_active': target_user.is_active,
                    }
                else:
                    # HELPER: simple_error_response - Sin permisos
                    return simple_error_response('No autorizado para ver este usuario', 403)
        
        else:
            if current_user_id != user_id:
                # HELPER: simple_error_response - Sin permisos
                return simple_error_response('No autorizado para ver este usuario', 403)
            
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
        
        # HELPER: simple_success_response - Respuesta exitosa
        return simple_success_response(user_data, f'Detalles del usuario {user_id}')
    
    if request.method == 'PUT':
        if not is_admin and current_user_id != user_id:
            # HELPER: simple_error_response - Sin permisos para actualizar
            return simple_error_response('No autorizado para actualizar este usuario', 403)
        
        # HELPER: validate_request_json - Validar datos recibidos
        data, error_response, status = validate_request_json()
        if error_response:
            return error_response, status
        
        admin_only_fields = ['is_admin', 'role', 'current_points', 'trial_end_date', 'is_active']
        if not is_admin:
            for field in admin_only_fields:
                if field in data:
                    # HELPER: simple_error_response - Sin permisos para modificar campo
                    return simple_error_response(f'No autorizado para modificar {field}', 403)
        
        if 'email' in data and data['email'] != target_user.email:
            existing = db.session.execute(
                db.select(Users).where(Users.email == data['email'])
            ).scalar()
            if existing:
                # HELPER: simple_error_response - Email ya existe
                return simple_error_response('El email ya está registrado', 409)
        
        if 'first_name' in data:
            target_user.first_name = data['first_name'].strip()
        if 'last_name' in data:
            target_user.last_name = data['last_name'].strip()
        if 'email' in data:
            target_user.email = data['email'].strip().lower()
        
        if is_admin:
            if 'role' in data:
                target_user.role = data['role']
            if 'current_points' in data:
                points = data['current_points']
                if not isinstance(points, int) or points < 0:
                    # HELPER: simple_error_response - Puntos inválidos
                    return simple_error_response('Los puntos deben ser un número entero no negativo', 400)
                target_user.current_points = points
            if 'is_active' in data:
                target_user.is_active = bool(data['is_active'])
            if 'is_admin' in data:
                target_user.is_admin = bool(data['is_admin'])
            if 'trial_end_date' in data:
                try:
                    trial_date = datetime.fromisoformat(data['trial_end_date'].replace('Z', '+00:00'))
                    target_user.trial_end_date = trial_date
                except ValueError:
                    # HELPER: simple_error_response - Fecha inválida
                    return simple_error_response('Formato de fecha inválido para trial_end_date', 400)
        
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
        
        # HELPER: simple_success_response - Usuario actualizado
        return simple_success_response(response_data, f'Usuario {user_id} actualizado')
    
    if request.method == 'DELETE':
        if not is_admin:
            # HELPER: simple_error_response - Solo admin puede eliminar
            return simple_error_response('Solo administradores pueden eliminar usuarios', 403)
        
        if current_user_id == user_id:
            # HELPER: simple_error_response - No puede eliminarse a sí mismo
            return simple_error_response('No puedes eliminarte a ti mismo', 400)
        
        db.session.delete(target_user)
        db.session.commit()
        
        # HELPER: simple_success_response - Usuario eliminado
        return simple_success_response({}, f'Usuario {user_id} eliminado')
    
    # HELPER: method_not_allowed_response - Método no permitido
    return method_not_allowed_response()

# POST: Cambiar contraseña de usuario
@api.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    # HELPER: validate_user_role - Verificar usuario autenticado
    user, response_body_validation, status = validate_user_role()
    if response_body_validation:
        return response_body_validation, status
    
    user_id = user.get('user_id')
    
    # HELPER: validate_request_json - Validar contraseñas
    data, error_response, status = validate_request_json(['current_password', 'new_password'])
    if error_response:
        return error_response, status
    
    db_user = db.session.execute(db.select(Users).where(Users.user_id == user_id)).scalar()
    
    if not db_user:
        # HELPER: simple_error_response - Usuario no encontrado
        return simple_error_response('Usuario no encontrado', 404)
    
    current_password = data.get('current_password', '')
    new_password = data.get('new_password', '')
    
    if not check_password_hash(db_user.password_hash, current_password):
        # HELPER: simple_error_response - Contraseña incorrecta
        return simple_error_response('Contraseña actual incorrecta', 401)
    
    if not new_password:
        # HELPER: simple_error_response - Nueva contraseña vacía
        return simple_error_response('La nueva contraseña no puede estar vacía', 400)
    
    if len(new_password) < 8:
        # HELPER: simple_error_response - Contraseña muy corta
        return simple_error_response('La nueva contraseña debe tener al menos 8 caracteres', 400)
    
    if check_password_hash(db_user.password_hash, new_password):
        # HELPER: simple_error_response - Contraseña igual a la actual
        return simple_error_response('La nueva contraseña no puede ser igual a la actual', 400)
    
    db_user.password_hash = generate_password_hash(new_password)
    db.session.commit()
    
    # HELPER: simple_success_response - Contraseña actualizada
    return simple_success_response(
        {
            'user_id': user_id,
            'password_changed': True
        },
        'Contraseña actualizada exitosamente'
    )

# POST: Eliminar cuenta propia
@api.route('/delete-my-account', methods=['POST'])
@jwt_required()
def delete_my_account():
    # HELPER: validate_user_role - Verificar usuario autenticado
    user, response_body_validation, status = validate_user_role()
    if response_body_validation:
        return response_body_validation, status
    
    user_id = user.get('user_id')
    
    # HELPER: validate_request_json - Validar confirmación
    data, error_response, status = validate_request_json(['password', 'confirmation'])
    if error_response:
        return error_response, status
    
    db_user = db.session.execute(db.select(Users).where(Users.user_id == user_id)).scalar()
    
    if not db_user:
        # HELPER: simple_error_response - Usuario no encontrado
        return simple_error_response('Usuario no encontrado', 404)
    
    password = data.get('password', '')
    confirmation = data.get('confirmation', '').strip().lower()
    
    if not check_password_hash(db_user.password_hash, password):
        # HELPER: simple_error_response - Contraseña incorrecta
        return simple_error_response('Contraseña incorrecta', 401)
    
    if confirmation != 'eliminar mi cuenta':
        # HELPER: simple_error_response - Confirmación incorrecta
        return simple_error_response('Debes escribir "eliminar mi cuenta" para confirmar', 400)
    
    db_user.is_active = False
    db_user.original_email = db_user.email
    deletion_uuid = uuid.uuid4().hex[:8]
    new_email = f"deleted_{deletion_uuid}_{user_id}@deleted.local"
    
    if len(new_email) > 100:
        new_email = f"deleted_{deletion_uuid}@deleted.local"
    
    db_user.email = new_email
    db_user.deletion_uuid = deletion_uuid
    db_user.deleted_at = datetime.now(timezone.utc)
    
    db.session.commit()
    
    # HELPER: simple_success_response - Cuenta eliminada
    return simple_success_response(
        {
            'account_deleted': True,
            'user_id': user_id,
            'deleted_at': datetime.now(timezone.utc).isoformat(),
            'deletion_id': deletion_uuid,
            'note': 'El email ha sido reemplazado con uno único para evitar conflictos. Tu email original se ha archivado de forma segura.'
        },
        'Cuenta eliminada exitosamente'
    )

# GET: Listar cursos públicos (sin autenticación)
@api.route('/courses-public', methods=['GET'])
def courses_public():
    
    # HELPER: method_not_allowed_response - Verificar método
    if request.method != 'GET':
        return method_not_allowed_response()
    
    # HELPER: build_pagination_params - Obtener parámetros de paginación
    page, per_page, offset = build_pagination_params(request)
    
    # Contar cursos activos
    total_count = db.session.execute(
        db.select(db.func.count()).select_from(Courses)
        .where(Courses.is_active == True)
    ).scalar()
    
    # Obtener cursos paginados
    courses = db.session.execute(
        db.select(Courses)
        .where(Courses.is_active == True)
        .order_by(Courses.course_id)
        .limit(per_page)
        .offset(offset)
    ).scalars()
    
    # Convertir a JSON usando serialize() del modelo CORREGIDO
    results = [course.serialize() for course in courses]
    
    # HELPER: build_pagination_response - Enviar respuesta paginada
    return build_pagination_response(
        results=results,
        total_count=total_count,
        page=page,
        per_page=per_page,
        message='Listado de cursos disponibles'
    )

# GET/POST: Operaciones CRUD de cursos (privado, requiere autenticación)
@api.route('/courses-private', methods=['GET', 'POST'])
@jwt_required()
def courses_private():
    # HELPER: validate_user_role - Verificar usuario autenticado
    user, response_body_validation, status = validate_user_role()
    if response_body_validation:
        return response_body_validation, status
    
    is_admin = user.get('is_admin', False)
    user_role = user.get('role')
    user_id = user.get('user_id')
    
    if request.method == 'GET':
        # HELPER: build_pagination_params - Obtener parámetros de paginación
        page, per_page, offset = build_pagination_params(request)
        
        total_query = db.session.execute(db.select(db.func.count()).select_from(Courses)).scalar()
        
        rows = db.session.execute(db.select(Courses).order_by(Courses.course_id).limit(per_page).offset(offset)).scalars()
        
        results = [row.serialize() for row in rows]
        
        # HELPER: build_pagination_response - Enviar respuesta paginada
        return build_pagination_response(
            results=results,
            total_count=total_query,
            page=page,
            per_page=per_page,
            message='Listado de cursos (privado)'
        )

    if request.method == 'POST':
        if not is_admin and user_role != 'teacher':
            # HELPER: simple_error_response - Sin permisos para crear
            return simple_error_response('No autorizado para crear cursos, no es Administrador ni profesor', 403)
        
        # HELPER: validate_request_json - Validar datos del curso
        data, error_response, status = validate_request_json(['title', 'price', 'points'])
        if error_response:
            return error_response, status
        
        price = data.get('price')
        if not isinstance(price, (int, float)) or price < 0:
            # HELPER: simple_error_response - Precio inválido
            return simple_error_response('El precio debe ser un número mayor o igual a 0', 400)
        
        points = data.get('points')
        if not isinstance(points, (int, float)) or points < 0:
            # HELPER: simple_error_response - Puntos inválidos
            return simple_error_response('Los puntos deben ser un número mayor o igual a 0', 400)
        
        row = Courses(title=data.get('title', '').strip(),
                      description=data.get('description', 'info no disponible').strip(),
                      price=price,
                      is_active=data.get('is_active', True),
                      points=points,
                      created_by=user_id)
        
        db.session.add(row)
        db.session.commit()

        # HELPER: simple_success_response - Curso creado
        return simple_success_response(row.serialize(), 'Curso creado exitosamente'), 201
    
    # HELPER: method_not_allowed_response - Método no permitido
    return method_not_allowed_response()

# GET/PUT/DELETE: Operaciones CRUD para curso específico
@api.route('/courses-private/<int:course_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def course_private(course_id):
    # HELPER: validate_user_role - Verificar usuario autenticado
    user, response_body_validation, status = validate_user_role()
    if response_body_validation:
        return response_body_validation, status
    
    user_id = user.get('user_id')
    is_admin = user.get('is_admin', False)
    user_role = user.get('role')

    row = db.session.execute(db.select(Courses).where(Courses.course_id == course_id)).scalar()
    
    if not row:
        # HELPER: simple_error_response - Curso no encontrado
        return simple_error_response(f'Curso {course_id} no encontrado', 404)

    if request.method == 'GET':
        # HELPER: simple_success_response - Detalles del curso
        return simple_success_response(row.serialize(), f'Detalles del curso {course_id}')

    if request.method == 'PUT':
        if not is_admin:
            if user_role != 'teacher':
                # HELPER: simple_error_response - No es admin ni teacher
                return simple_error_response('No eres un Administrador ni profesor, no puedes actualizar cursos', 403)
            if row.created_by != user_id:
                # HELPER: simple_error_response - No es el creador del curso
                return simple_error_response('No puedes actualizar cursos de otros profesores', 403)

        # HELPER: validate_request_json - Validar datos de actualización
        data, error_response, status = validate_request_json()
        if error_response:
            return error_response, status

        if 'price' in data:
            price = data['price']
            if not isinstance(price, (int, float)) or price < 0:
                # HELPER: simple_error_response - Precio inválido
                return simple_error_response('El precio debe debe de ser un número mayor o igual a 0', 400)
            row.price = price
        
        if 'points' in data:
            points = data['points']
            if not isinstance(points, (int, float)) or points < 0:
                # HELPER: simple_error_response - Puntos inválidos
                return simple_error_response('Los puntos deben ser un número mayor o igual a 0', 400)
            row.points = points
        
        if 'title' in data:
            row.title = data['title'].strip()
        if 'description' in data:
            row.description = data['description'].strip()
        if 'is_active' in data:
            row.is_active = bool(data['is_active'])

        db.session.commit()
        
        # HELPER: simple_success_response - Curso actualizado
        return simple_success_response(row.serialize(), f'Curso {course_id} Actualizado')

    if request.method == 'DELETE':
        if not is_admin:
            if user_role != 'teacher':
                # HELPER: simple_error_response - No es admin ni teacher
                return simple_error_response('No eres un administrador o profesor, no puedes eliminar cursos', 403)
            if row.created_by != user_id:
                # HELPER: simple_error_response - No es el creador del curso
                return simple_error_response('No puedes eliminar cursos de otros profesores', 403)
        
        db.session.delete(row)
        db.session.commit()
        
        # HELPER: simple_success_response - Curso eliminado
        return simple_success_response({}, f'Curso {course_id} Eliminado')
    
    # HELPER: method_not_allowed_response - Método no permitido
    return method_not_allowed_response()

# GET: Listar módulos públicos (sin autenticación)
@api.route('/modules-public', methods=['GET'])
def modules_public():
    
    # HELPER: method_not_allowed_response - Verificar método
    if request.method != 'GET':
        return method_not_allowed_response()
    
    # HELPER: build_pagination_params - Obtener parámetros de paginación
    page, per_page, offset = build_pagination_params(request)
    
    # Contar total de módulos
    total_count = db.session.execute(
        db.select(db.func.count()).select_from(Modules)
    ).scalar()
    
    # Obtener módulos paginados
    modules = db.session.execute(
        db.select(Modules)
        .order_by(Modules.module_id)
        .limit(per_page)
        .offset(offset)
    ).scalars()
    
    # Convertir a JSON
    results = [module.serialize() for module in modules]
    
    # HELPER: build_pagination_response - Enviar respuesta paginada
    return build_pagination_response(
        results=results,
        total_count=total_count,
        page=page,
        per_page=per_page,
        message='Listado de módulos'
    )

# GET/POST: Operaciones CRUD de módulos (privado, requiere autenticación)
@api.route('/modules-private', methods=['GET', 'POST'])
@jwt_required()
def modules_private():
    # HELPER: validate_user_role - Verificar usuario autenticado
    user, response_body_validation, status = validate_user_role()
    if response_body_validation:
        return response_body_validation, status
    
    user_id = user.get('user_id')
    is_admin = user.get('is_admin', False)
    user_role = user.get('role')

    if request.method == 'GET':
        # HELPER: build_pagination_params - Obtener parámetros de paginación
        page, per_page, offset = build_pagination_params(request)
        
        total_query = db.session.execute(db.select(db.func.count()).select_from(Modules)).scalar()
        
        rows = db.session.execute(db.select(Modules).order_by(Modules.module_id).limit(per_page).offset(offset)).scalars()
        
        results = [row.serialize() for row in rows]
        
        # HELPER: build_pagination_response - Enviar respuesta paginada
        return build_pagination_response(
            results=results,
            total_count=total_query,
            page=page,
            per_page=per_page,
            message='Listado de módulos'
        )

    if request.method == 'POST':
        if not is_admin and user_role != 'teacher':
            # HELPER: simple_error_response - Sin permisos para crear
            return simple_error_response('No autorizado para crear módulos, no es Administrador ni profesor', 403)
        
        # HELPER: validate_request_json - Validar datos del módulo
        data, error_response, status = validate_request_json(['title', 'order', 'points', 'course_id'])
        if error_response:
            return error_response, status
        
        # Validar course_id
        course_id = data.get('course_id')
        
        course = db.session.execute(db.select(Courses).where(Courses.course_id == course_id)).scalar()
        if not course:
            # HELPER: simple_error_response - Curso no encontrado
            return simple_error_response('Curso no encontrado', 400)

        # Validar order (debe ser int ≥ 0)
        order = data.get('order')
        if not isinstance(order, int) or order < 0:
            return simple_error_response('El orden debe ser un número entero no negativo', 400)
        
        # Validar points (debe ser numérico ≥ 0)
        points = data.get('points')
        if not isinstance(points, (int, float)) or points < 0:
            return simple_error_response('Los puntos deben ser un número mayor o igual a 0', 400)
        
        # Validar título no vacío
        title = data.get('title', '').strip()
        if not title:
            return simple_error_response('El título del módulo no puede estar vacío', 400)
        
        # Verificar unicidad de orden en el curso
        existing_module = db.session.execute(
            db.select(Modules).where(Modules.course_id == course_id, Modules.order == order)).scalar()
        
        if existing_module:
            return simple_error_response(f'Ya existe un módulo con el orden {order} en este curso', 409)
        
        # Crear módulo
        row = Modules(
            title=title,
            order=order,
            points=points,
            course_id=course_id,
            is_active=True
        )
        
        db.session.add(row)
        db.session.commit()

        # HELPER: simple_success_response - Módulo creado
        return simple_success_response(row.serialize(), 'Módulo creado exitosamente'), 201
    
    # HELPER: method_not_allowed_response - Método no permitido
    return method_not_allowed_response()

# GET/PUT/DELETE: Operaciones CRUD para módulo específico
@api.route('/modules-private/<int:module_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def module_private(module_id):

    # HELPER: validate_user_role - Verificar usuario autenticado
    user, response_body_validation, status = validate_user_role()
    if response_body_validation:
        return response_body_validation, status
       
    row = db.session.execute(db.select(Modules).where(Modules.module_id == module_id)).scalar()
    
    if not row:
        # HELPER: simple_error_response - Módulo no encontrado
        return simple_error_response('Módulo no encontrado', 404)

    if request.method == 'GET':
        # HELPER: simple_success_response - Detalles del módulo
        return simple_success_response(row.serialize(), f'Detalles del módulo {module_id}')

    if request.method == 'PUT':
        if not user.get('is_admin'):
            if user.get('role') != 'teacher':
                # HELPER: simple_error_response - No es admin ni teacher
                return simple_error_response('Solo el administrador y profesor pueden actualizar módulos', 403)
        
        if user.get('role') == 'teacher' and not user.get('is_admin'):
            course_owner = db.session.execute(db.select(Courses).where(Courses.course_id == row.course_id,Courses.created_by == user.get('user_id'))).scalar()
            if not course_owner:
                # HELPER: simple_error_response - No es el creador del curso
                return simple_error_response('No tienes permiso para modificar módulos de este curso', 403)

        # HELPER: validate_request_json - Validar datos de actualización
        data, error_response, status = validate_request_json()
        if error_response:
            return error_response, status

        if 'course_id' in data:
            course = db.session.execute(db.select(Courses).where(Courses.course_id == data.get('course_id'))).scalar()
            if not course:
                # HELPER: simple_error_response - Curso no encontrado
                return simple_error_response('Curso no encontrado', 400)
        
        target_course_id = data.get('course_id', row.course_id)

        if 'order' in data:
            existing_module = db.session.execute(db.select(Modules).where(Modules.course_id == target_course_id,
                                                                          Modules.order == data.get('order'),
                                                                          Modules.module_id != module_id)).scalar()
            if existing_module:
                # HELPER: simple_error_response - Orden duplicado
                return simple_error_response(f'Ya existe un módulo con el orden {data.get("order")} en este curso', 409)
        
        if 'points' in data:
            points = data['points']
            if not isinstance(points, (int, float)) or points < 0:
                # HELPER: simple_error_response - Puntos inválidos
                return simple_error_response('Los puntos deben ser un número mayor o igual a 0', 400)
            row.points = points
        
        if 'title' in data:
            row.title = data.get('title', row.title)
        if 'order' in data:
            row.order = data.get('order', row.order)
        if 'course_id' in data:
            row.course_id = data.get('course_id', row.course_id)

        db.session.commit()
        # HELPER: simple_success_response - Módulo actualizado
        return simple_success_response(row.serialize(), f'Módulo {module_id} actualizado')

    if request.method == 'DELETE':
        if not user.get('is_admin'):
            if user.get('role') != 'teacher':
                # HELPER: simple_error_response - No es admin ni teacher
                return simple_error_response('No eres un Admin ni Teacher, no puedes eliminar Modulos', 403)
        
        if user.get('role') == 'teacher' and not user.get('is_admin'):
            course_owner = db.session.execute(db.select(Courses)
                                              .where(Courses.course_id == row.course_id,Courses.created_by == user.get('user_id'))).scalar()
            if not course_owner:
                # HELPER: simple_error_response - No es el creador del curso
                return simple_error_response('No tienes permiso para eliminar módulos de este curso', 403)

        db.session.delete(row)
        db.session.commit()
        # HELPER: simple_success_response - Módulo eliminado
        return simple_success_response({}, f'Módulo {module_id} eliminado')
    
    # HELPER: method_not_allowed_response - Método no permitido
    return method_not_allowed_response()

# GET: Listar lecciones públicas (sin autenticación)
@api.route('/lessons-public', methods=['GET'])
def lessons_public():
    
    # HELPER: method_not_allowed_response - Verificar método
    if request.method != 'GET':
        return method_not_allowed_response()
    
    # HELPER: build_pagination_params - Obtener parámetros de paginación
    page, per_page, offset = build_pagination_params(request)
    
    # Contar total de lecciones
    total_count = db.session.execute(
        db.select(db.func.count()).select_from(Lessons)
    ).scalar()
    
    # Obtener lecciones paginadas
    lessons = db.session.execute(
        db.select(Lessons)
        .order_by(Lessons.lesson_id)
        .limit(per_page)
        .offset(offset)
    ).scalars()
    
    # Convertir a JSON
    results = [lesson.serialize() for lesson in lessons]
    
    # HELPER: build_pagination_response - Enviar respuesta paginada
    return build_pagination_response(
        results=results,
        total_count=total_count,
        page=page,
        per_page=per_page,
        message='Listado de lecciones'
    )

# GET/POST: Operaciones CRUD de lecciones (privado, requiere autenticación)
@api.route('/lessons-private', methods=['GET', 'POST'])
@jwt_required()
def lessons_private():
    # HELPER: validate_user_role - Verificar usuario autenticado
    user, response_body_validation, status = validate_user_role()
    if response_body_validation:
        return response_body_validation, status

    is_admin = user.get('is_admin', False)
    user_role = user.get('role')
    user_id = user.get('user_id')

    if request.method == 'GET':
        # HELPER: build_pagination_params - Obtener parámetros de paginación
        page, per_page, offset = build_pagination_params(request)

        total = db.session.execute(
            db.select(db.func.count()).select_from(Lessons)
        ).scalar()

        lessons = db.session.execute(
            db.select(Lessons)
            .order_by(Lessons.lesson_id)
            .limit(per_page)
            .offset(offset)
        ).scalars()

        results = []
        for lesson in lessons:
            data = lesson.serialize()

            multimedia = db.session.execute(
                db.select(MultimediaResources)
                .where(MultimediaResources.lesson_id == lesson.lesson_id)
                .order_by(MultimediaResources.order)
            ).scalars()

            data["multimedia_resources"] = [m.serialize() for m in multimedia]
            results.append(data)

        # HELPER: build_pagination_response - Enviar respuesta paginada
        return build_pagination_response(
            results=results,
            total_count=total,
            page=page,
            per_page=per_page,
            message="Listado de lecciones"
        )

    if request.method == 'POST':
        if not is_admin and user_role != 'teacher':
            # HELPER: simple_error_response - Sin permisos para crear
            return simple_error_response("No autorizado para crear lecciones", 403)

        content_type = request.content_type or ""

        if "multipart/form-data" in content_type:
            return _handle_multipart_upload(request, user_id, user)

        return _handle_json_create(request, user_id, user)

    # HELPER: method_not_allowed_response - Método no permitido
    return method_not_allowed_response()

# GET/PUT/DELETE: Operaciones CRUD para lección específica
@api.route('/lessons/<int:lesson_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def lesson_detail(lesson_id):
    # HELPER: validate_user_role - Verificar usuario autenticado
    user, response_body_validation, status = validate_user_role()
    if response_body_validation:
        return response_body_validation, status

    user_id = user.get('user_id')
    is_admin = user.get('is_admin', False)
    user_role = user.get('role')
    
    lesson = db.session.execute(
        db.select(Lessons).where(Lessons.lesson_id == lesson_id)
    ).scalar()

    if not lesson:
        # HELPER: simple_error_response - Lección no encontrada
        return simple_error_response(f"Lección {lesson_id} no encontrada", 404)

    if request.method == 'GET':
        lesson_data = lesson.serialize()

        multimedia = db.session.execute(
            db.select(MultimediaResources)
            .where(MultimediaResources.lesson_id == lesson.lesson_id)
            .order_by(MultimediaResources.order)
        ).scalars()

        lesson_data["multimedia_resources"] = [m.serialize() for m in multimedia]

        # HELPER: simple_success_response - Detalles de la lección
        return simple_success_response(lesson_data, f"Detalles de la lección {lesson_id}")

    if request.method == 'PUT':
        if not is_admin and user_role != 'teacher':
            # HELPER: simple_error_response - Sin permisos para actualizar
            return simple_error_response("No autorizado para actualizar lecciones", 403)

        if user_role == 'teacher' and not is_admin:
            module = db.session.execute(
                db.select(Modules).where(Modules.module_id == lesson.module_id)
            ).scalar()

            if module:
                course = db.session.execute(
                    db.select(Courses).where(Courses.course_id == module.course_id)
                ).scalar()

                if not course or course.created_by != user_id:
                    # HELPER: simple_error_response - No es el creador del curso
                    return simple_error_response("No autorizado para actualizar lecciones de otros profesores", 403)

        content_type = request.content_type or ""

        if "multipart/form-data" in content_type:
            return _handle_multipart_upload(request, user_id, user)

        # HELPER: validate_request_json - Validar datos de actualización
        data, error_response, status = validate_request_json()
        if error_response:
            return error_response, status
        
        if 'title' in data:
            lesson.title = data['title'].strip()
        if 'content' in data:
            lesson.content = data['content'].strip()
        if 'learning_objective' in data:
            lesson.learning_objective = data['learning_objective'].strip()
        if 'signs_taught' in data:
            lesson.signs_taught = data['signs_taught'].strip()
        if 'order' in data:
            lesson.order = data['order']
        if 'trial_visible' in data:
            lesson.trial_visible = bool(data['trial_visible'])
        if 'is_active' in data:
            lesson.is_active = bool(data['is_active'])
        
        db.session.commit()
        
        # HELPER: simple_success_response - Lección actualizada
        return simple_success_response(lesson.serialize(), f"Lección {lesson_id} actualizada")

    if request.method == 'DELETE':
        if not is_admin and user_role != 'teacher':
            # HELPER: simple_error_response - Sin permisos para eliminar
            return simple_error_response("No autorizado para eliminar lecciones", 403)

        if user_role == 'teacher' and not is_admin:
            module = db.session.execute(
                db.select(Modules).where(Modules.module_id == lesson.module_id)
            ).scalar()

            if module:
                course = db.session.execute(
                    db.select(Courses).where(Courses.course_id == module.course_id)
                ).scalar()

                if not course or course.created_by != user_id:
                    # HELPER: simple_error_response - No es el creador del curso
                    return simple_error_response("No autorizado para eliminar lecciones de otros profesores", 403)

        db.session.delete(lesson)
        db.session.commit()
        
        # HELPER: simple_success_response - Lección eliminada
        return simple_success_response({}, f"Lección {lesson_id} eliminada")

    # HELPER: method_not_allowed_response - Método no permitido
    return method_not_allowed_response()

# POST: Verificar curso para compra (público)
@api.route('/purchases-public', methods=['POST'])
def purchases_public():
    # HELPER: validate_request_json - Validar datos de compra
    data, error_response, status = validate_request_json(['course_id'])
    if error_response:
        return error_response, status
    
    course_id = data.get('course_id')
    if not isinstance(course_id, int) or course_id < 1:
        # HELPER: simple_error_response - ID inválido
        return simple_error_response('ID de curso inválido. Debe ser un número positivo.', 400)
    
    course = db.session.execute(
        db.select(Courses)
        .where(
            Courses.course_id == course_id,
            Courses.is_active == True
        )
    ).scalar()
    
    if not course:
        # HELPER: simple_error_response - Curso no disponible
        return simple_error_response('Curso no disponible en este momento', 404)
    
    stripe_config = stripe_service.get_stripe_config()
    
    payment_info = {
        'requires_payment': course.price > 0,
        'amount': float(course.price),
        'currency': stripe_config['currency'],
        'payment_methods': ['card']
    }
    
    if course.price > 0:
        payment_info.update({
            'amount_cents': stripe_service.format_amount_for_stripe(course.price),
            'stripe_public_key': stripe_config['publishable_key'],
            'instructions': 'Pago seguro con tarjeta de crédito/débito vía Stripe'
        })
    else:
        payment_info.update({
            'instructions': 'Curso gratuito - solo requiere registro'
        })
    
    response_body = {
        'message': '¡Excelente elección! Para acceder a este curso necesitas una cuenta.',
        'results': {
            'action_required': 'registration',
            'course_details': {
                'course_id': course.course_id,
                'title': course.title,
                'description': course.description,
                'price': float(course.price) if course.price else 0,
                'points_reward': course.points,
                'created_by': course.created_by,
                'is_free': course.price == 0
            },
            'payment_info': payment_info,
            'benefits': [
                'Acceso completo al curso',
                'Seguimiento de tu progreso',
                'Obtención de puntos y logros',
                'Soporte de profesores'
            ]
        },
        'next_steps': [
            '1. Regístrate como usuario nuevo',
            '2. Inicia sesión con tus credenciales',
            '3. Procede con la compra del curso'
        ]
    }
    
    if course.price == 0:
        response_body['message'] = '¡Curso gratuito! Regístrate para acceder inmediatamente.'
        response_body['results']['special_note'] = 'Este curso es completamente gratuito'
    
    # HELPER: simple_success_response - Info de compra
    return simple_success_response(response_body['results'], response_body['message'])

# GET/POST: Operaciones CRUD de compras (privado, requiere autenticación)
@api.route('/purchases-private', methods=['GET', 'POST'])
@jwt_required()
def purchases_private():
    user, error_response, status = validate_user_role()
    if error_response:
        return error_response, status
    
    user_id = user.get('user_id')
    is_admin = user.get('is_admin', False)
    user_role = user.get('role')
    user_email = user.get('email', '')
    
    if request.method == 'GET':
        page, per_page, offset = build_pagination_params(request)
        
        data_query = db.select(Purchases)
        count_query = db.select(db.func.count()).select_from(Purchases)
        
        if not is_admin:
            if user_role == 'teacher':
                data_query = data_query.join(Courses, Purchases.course_id == Courses.course_id) \
                                       .where(Courses.created_by == user_id)
                
                count_query = count_query.join(Courses, Purchases.course_id == Courses.course_id) \
                                         .where(Courses.created_by == user_id)
            else:
                data_query = data_query.where(Purchases.user_id == user_id)
                count_query = count_query.where(Purchases.user_id == user_id)
        
        total_count = db.session.execute(count_query).scalar() or 0
        
        rows = db.session.execute(
            data_query.order_by(Purchases.purchase_date.desc())
            .limit(per_page)
            .offset(offset)
        ).scalars()
        
        results = [row.serialize() for row in rows]
        
        return build_pagination_response(
            results=results,
            total_count=total_count,
            page=page,
            per_page=per_page,
            message='Listado de compras' if results else 'No hay compras registradas'
        )
    
    if request.method == 'POST':
        # HELPER: validate_request_json - Validar datos de compra
        data, error_response, status = validate_request_json(['course_id'])
        if error_response:
            return error_response, status
        
        course_id = data.get('course_id')
        
        if not isinstance(course_id, int) or course_id < 1:
            return simple_error_response('ID de curso inválido. Debe ser un número positivo.', 400)
        
        course = db.session.execute(
            db.select(Courses).where(
                Courses.course_id == course_id,
                Courses.is_active == True
            )
        ).scalar()
        
        if not course:
            return simple_error_response('Curso no encontrado o inactivo', 400)
        
        existing_purchase = db.session.execute(
            db.select(Purchases).where(
                Purchases.user_id == user_id,
                Purchases.course_id == course_id,
                Purchases.status == 'paid'
            )
        ).scalar()
        
        if existing_purchase:
            return simple_error_response('Ya tienes este curso comprado', 409)
        
        if course.price == 0:
            purchase = Purchases(
                purchase_date=datetime.now(timezone.utc),
                price=0,
                total=0,
                status='paid',
                start_date=datetime.now(timezone.utc),
                course_id=course_id,
                user_id=user_id
            )
            
            db.session.add(purchase)
            db.session.flush()
            
            if course.points > 0:
                user_point = UserPoints(
                    user_id=user_id,
                    points=course.points,
                    point_type='course',
                    event_description=f"Curso gratuito: {course.title}",
                    date=datetime.now(timezone.utc)
                )
                db.session.add(user_point)
                
                user_obj = db.session.get(Users, user_id)
                if user_obj:
                    current = user_obj.current_points or 0
                    user_obj.current_points = current + course.points
            
            db.session.commit()
            
            return simple_success_response(
                purchase.serialize(),
                '¡Curso gratuito activado exitosamente!'
            ), 201
        
        purchase = Purchases(
            purchase_date=datetime.now(timezone.utc),
            price=course.price,
            total=course.price,
            status='pending',
            start_date=None,
            course_id=course_id,
            user_id=user_id
        )
        
        db.session.add(purchase)
        db.session.flush()
        
        metadata = stripe_service.create_metadata_for_purchase(
            purchase_id=purchase.purchase_id,
            user_id=user_id,
            course_id=course.course_id,
            course_title=course.title
        )
        
        amount_cents = stripe_service.format_amount_for_stripe(course.price)
        
        if amount_cents < 50:
            db.session.rollback()
            return simple_error_response("Monto muy bajo para pago con tarjeta. Mínimo: $0.50 USD", 400)
        
        payment_result = stripe_service.create_payment_intent(
            amount_cents=amount_cents,
            currency='usd',
            metadata=metadata,
            description=f"Compra del curso: {course.title}",
            customer_email=user_email
        )
        
        if not payment_result['success']:
            db.session.rollback()
            return simple_error_response(payment_result.get('error', 'Error de Stripe'), 500)
        
        purchase.stripe_payment_intent_id = payment_result['id']
        db.session.commit()
        
        stripe_config = stripe_service.get_stripe_config()
        
        return simple_success_response(
            {
                'purchase': purchase.serialize(),
                'stripe_payment': {
                    'client_secret': payment_result['client_secret'],
                    'payment_intent_id': payment_result['id'],
                    'amount': amount_cents,
                    'amount_display': f"${amount_cents/100:.2f}",
                    'currency': 'usd',
                    'publishable_key': stripe_config['publishable_key']
                },
                'course': {
                    'id': course.course_id,
                    'title': course.title,
                    'description': course.description,
                    'price': float(course.price),
                    'points': course.points
                }
            },
            'Pago preparado exitosamente'
        ), 201
    
    return method_not_allowed_response()

# GET/PUT/DELETE: Operaciones CRUD para compra específica
@api.route('/purchases/<int:purchase_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def purchase_detail(purchase_id):
    # HELPER: validate_user_role - Verificar usuario autenticado
    user, error_response, status = validate_user_role()
    if error_response:
        return error_response, status
    
    user_id = user.get('user_id')
    is_admin = user.get('is_admin', False)
    user_role = user.get('role')
    user_email = user.get('email', '')
    
    purchase = db.session.execute(
        db.select(Purchases).where(Purchases.purchase_id == purchase_id)
    ).scalar()

    if not purchase:
        # HELPER: simple_error_response - Compra no encontrada
        return simple_error_response(f'Compra {purchase_id} no encontrada', 404)
    
    if request.method == 'GET':
        if not is_admin:
            if user_role == 'teacher':
                if user_id != purchase.user_id:
                    is_teacher_student = db.session.execute(
                        db.select(Purchases)
                        .join(Courses, Purchases.course_id == Courses.course_id)
                        .where(
                            Purchases.purchase_id == purchase_id,
                            Courses.created_by == user_id
                        )
                    ).scalar()
                    
                    if not is_teacher_student:
                        # HELPER: simple_error_response - Sin permisos para ver
                        return simple_error_response('No autorizado para ver esta compra', 403)
            else:
                if user_id != purchase.user_id:
                    # HELPER: simple_error_response - Sin permisos para ver
                    return simple_error_response('No autorizado para ver esta compra', 403)
        
        stripe_info = None
        if purchase.stripe_payment_intent_id:
            try:
                stripe_result = stripe_service.retrieve_payment_intent(
                    purchase.stripe_payment_intent_id
                )
                
                if stripe_result['success']:
                    payment_intent = stripe_result['payment_intent']
                    stripe_info = {
                        'status': payment_intent.status,
                        'amount': payment_intent.amount / 100,
                        'currency': payment_intent.currency,
                        'created': datetime.fromtimestamp(payment_intent.created, timezone.utc).isoformat(),
                        'payment_method': payment_intent.payment_method_types[0] if payment_intent.payment_method_types else None,
                        'customer_email': payment_intent.receipt_email,
                        'last_payment_error': payment_intent.last_payment_error.message if payment_intent.last_payment_error else None
                    }
                else:
                    stripe_info = {
                        'error': stripe_result.get('error', 'Error desconocido'),
                        'available': False
                    }
            except Exception as e:
                stripe_info = {
                    'error': str(e),
                    'available': False
                }
        
        course = db.session.execute(
            db.select(Courses).where(Courses.course_id == purchase.course_id)
        ).scalar()
        
        course_info = None
        if course:
            course_info = {
                'id': course.course_id,
                'title': course.title,
                'description': course.description,
                'price': float(course.price) if course.price else 0,
                'points': course.points,
                'is_active': course.is_active
            }
        
        buyer = db.session.execute(
            db.select(Users).where(Users.user_id == purchase.user_id)
        ).scalar()
        
        buyer_info = None
        if buyer:
            buyer_info = {
                'id': buyer.user_id,
                'email': buyer.email,
                'first_name': buyer.first_name,
                'last_name': buyer.last_name,
                'role': buyer.role,
                'current_points': buyer.current_points
            }
        
        purchase_data = purchase.serialize()
        
        # HELPER: simple_success_response - Detalles de la compra
        return simple_success_response(
            {
                'purchase': purchase_data,
                'stripe_info': stripe_info,
                'course': course_info,
                'buyer': buyer_info,
                'access_info': {
                    'can_edit': is_admin,
                    'can_delete': is_admin,
                    'viewed_by_admin': is_admin,
                    'viewed_by_owner': user_id == purchase.user_id,
                    'viewed_by_teacher': user_role == 'teacher' and user_id != purchase.user_id
                }
            },
            f'Detalles de la compra {purchase_id}'
        )
    
    if request.method == 'PUT':
        if not is_admin:
            # HELPER: simple_error_response - Solo admin puede modificar
            return simple_error_response('Solo administradores pueden modificar compras', 403)
        
        # HELPER: validate_request_json - Validar datos de actualización
        data, error_response, status = validate_request_json()
        if error_response:
            return error_response, status
        
        if not data:
            # HELPER: simple_error_response - Datos requeridos
            return simple_error_response('Request body requerido para actualizar', 400)
        
        immutable_fields = ['purchase_date', 'price', 'total', 'course_id']
        
        for field in immutable_fields:
            if field in data:
                # HELPER: simple_error_response - Campo inmutable
                return simple_error_response(f'El campo {field} no puede ser modificado después de creada la compra', 400)
        
        if 'status' in data:
            valid_statuses = ['paid', 'pending', 'cancelled']
            
            if data.get('status') not in valid_statuses:
                # HELPER: simple_error_response - Status inválido
                return simple_error_response(f'Status inválido. Valores permitidos: {", ".join(valid_statuses)}', 400)
            
            if data['status'] == 'paid' and not purchase.start_date:
                purchase.start_date = datetime.now(timezone.utc)
        
        if 'user_id' in data:
            new_user_id = data['user_id']
            
            if not isinstance(new_user_id, int) or new_user_id < 1:
                # HELPER: simple_error_response - User ID inválido
                return simple_error_response('user_id debe ser un número entero positivo', 400)
            
            new_user = db.session.execute(
                db.select(Users).where(Users.user_id == new_user_id)
            ).scalar()
            
            if not new_user:
                # HELPER: simple_error_response - Usuario no encontrado
                return simple_error_response('Usuario no encontrado', 400)
            
            if new_user_id != purchase.user_id:
                existing_purchase = db.session.execute(
                    db.select(Purchases).where(
                        Purchases.user_id == new_user_id,
                        Purchases.course_id == purchase.course_id,
                        Purchases.status == 'paid'
                    )
                ).scalar()
                
                if existing_purchase:
                    # HELPER: simple_error_response - Ya tiene el curso
                    return simple_error_response('El nuevo usuario ya tiene este curso comprado', 400)
            
            purchase.user_id = new_user_id
        
        if 'status' in data:
            purchase.status = data['status']
        
        if 'start_date' in data and data['start_date']:
            try:
                start_date_str = data['start_date'].replace('Z', '+00:00')
                start_date = datetime.fromisoformat(start_date_str)
                
                if start_date > datetime.now(timezone.utc):
                    # HELPER: simple_error_response - Fecha futura
                    return simple_error_response('start_date no puede ser una fecha futura', 400)
                
                purchase.start_date = start_date
            except (ValueError, AttributeError):
                # HELPER: simple_error_response - Formato de fecha inválido
                return simple_error_response('Formato de fecha inválido para start_date. Use formato ISO (ej: 2024-01-15T10:30:00Z)', 400)
        
        if 'stripe_payment_intent_id' in data:
            purchase.stripe_payment_intent_id = data['stripe_payment_intent_id']
        
        try:
            db.session.commit()
            
            if purchase.status == 'paid' and 'status' in data:
                course = db.session.execute(
                    db.select(Courses).where(Courses.course_id == purchase.course_id)
                ).scalar()
                
                if course and course.points > 0:
                    existing_points = db.session.execute(
                        db.select(UserPoints).where(
                            UserPoints.user_id == purchase.user_id,
                            UserPoints.event_description.contains(f"purchase_id:{purchase_id}")
                        )
                    ).scalar()
                    
                    if not existing_points:
                        user_point = UserPoints(
                            user_id=purchase.user_id,
                            points=course.points,
                            point_type='course',
                            event_description=f"Compra #{purchase_id} del curso: {course.title} | purchase_id:{purchase_id}",
                            date=datetime.now(timezone.utc)
                        )
                        db.session.add(user_point)
                        
                        buyer = db.session.get(Users, purchase.user_id)
                        if buyer:
                            current = buyer.current_points or 0
                            buyer.current_points = current + course.points
                        
                        db.session.commit()
            
            purchase_data = purchase.serialize()
            
            # HELPER: simple_success_response - Compra actualizada
            return simple_success_response(
                purchase_data,
                f'Compra {purchase_id} actualizada exitosamente'
            )
            
        except Exception as e:
            db.session.rollback()
            # HELPER: simple_error_response - Error al actualizar
            return simple_error_response(f'Error al actualizar la compra: {str(e)}', 500)
    
    if request.method == 'DELETE':
        if not is_admin:
            # HELPER: simple_error_response - Solo admin puede eliminar
            return simple_error_response('Solo administradores pueden eliminar compras', 403)
        
        if purchase.status == 'paid' and purchase.purchase_date:
            time_diff = datetime.now(timezone.utc) - purchase.purchase_date
            if time_diff.total_seconds() < 86400:
                # HELPER: simple_error_response - No se puede eliminar compra reciente
                return simple_error_response('No se pueden eliminar compras pagadas hace menos de 24 horas', 400)
        
        if purchase.stripe_payment_intent_id and purchase.status == 'pending':
            try:
                stripe_result = stripe_service.retrieve_payment_intent(purchase.stripe_payment_intent_id)
            except Exception as e:
                pass
        
        try:
            deleted_info = {
                'purchase_id': purchase_id,
                'course_id': purchase.course_id,
                'user_id': purchase.user_id,
                'status': purchase.status,
                'amount': float(purchase.total) if purchase.total else 0
            }
            
            db.session.delete(purchase)
            db.session.commit()
            
            # HELPER: simple_success_response - Compra eliminada
            return simple_success_response(
                {
                    'deleted': True,
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    **deleted_info
                },
                f'Compra {purchase_id} eliminada exitosamente'
            )
            
        except Exception as e:
            db.session.rollback()
            # HELPER: simple_error_response - Error al eliminar
            return simple_error_response(f'Error al eliminar la compra: {str(e)}', 500)
    
    # HELPER: method_not_allowed_response - Método no permitido
    return method_not_allowed_response()

@api.route('/points-ranking', methods=['GET'])
@jwt_required()
def points_ranking():
    user, error_response, status = validate_user_role()
    if error_response:
        return error_response, status
    
    user_id = user.get('user_id')
    is_admin = user.get('is_admin', False)
    user_role = user.get('role')
    
    page, per_page, offset = build_pagination_params(request)
    
    if is_admin:
        query = db.select(Users).where(Users.is_active == True)
        total = db.session.execute(db.select(db.func.count()).select_from(Users).where(Users.is_active == True)).scalar() or 0
        users = db.session.execute(query.order_by(Users.current_points.desc()).limit(per_page).offset(offset)).scalars()
        
        results = []
        for rank, user_obj in enumerate(users, 1):
            results.append({
                'rank': rank,
                'user_id': user_obj.user_id,
                'name': f"{user_obj.first_name} {user_obj.last_name}",
                'points': user_obj.current_points or 0
            })
        
        return build_pagination_response(results, total, page, per_page, 'Ranking general')
    
    elif user_role == 'teacher':
        query = db.select(Users).distinct() \
            .join(Purchases, Users.user_id == Purchases.user_id) \
            .join(Courses, Purchases.course_id == Courses.course_id) \
            .where(
                Courses.created_by == user_id,
                Users.role == 'student',
                Users.is_active == True,
                Purchases.status == 'paid'
            )
        
        total = db.session.execute(
            db.select(db.func.count(db.distinct(Users.user_id))) \
            .select_from(Users) \
            .join(Purchases, Users.user_id == Purchases.user_id) \
            .join(Courses, Purchases.course_id == Courses.course_id) \
            .where(
                Courses.created_by == user_id,
                Users.role == 'student',
                Users.is_active == True,
                Purchases.status == 'paid'
            )
        ).scalar() or 0
        
        students = db.session.execute(query.order_by(Users.current_points.desc()).limit(per_page).offset(offset)).scalars()
        
        results = []
        for rank, student in enumerate(students, 1):
            results.append({
                'rank': rank,
                'student_id': student.user_id,
                'name': f"{student.first_name} {student.last_name}",
                'points': student.current_points or 0
            })
        
        return build_pagination_response(results, total, page, per_page, 'Tus estudiantes')
    
    else:
        user_obj = db.session.execute(db.select(Users).where(Users.user_id == user_id)).scalar()
        return simple_success_response(
            {'points': user_obj.current_points if user_obj else 0},
            'Tus puntos'
        )

# GET/POST: Operaciones CRUD de puntos de usuario
@api.route('/user-points', methods=['GET', 'POST'])
@jwt_required()
def user_points():
    # HELPER: validate_user_role - Verificar usuario autenticado
    user, error_response, status = validate_user_role()
    if error_response:
        return error_response, status
    
    user_id = user.get('user_id')
    is_admin = user.get('is_admin', False)
    user_role = user.get('role')
    
    if request.method == 'GET':
        points_query = db.session.execute(db.select(UserPoints.user_id,
                                          func.sum(UserPoints.points).label('total_points'))
                                          .group_by(UserPoints.user_id)
                                          .order_by(func.sum(UserPoints.points).desc())).all()

        user_ids = [user_id for user_id, _ in points_query]
        users = db.session.execute(db.select(Users)
                                   .where(Users.user_id.in_(user_ids))).scalars()

        serialized_users = {user.user_id: user.serialize() for user in users}

        results = []
        for rank, (user_id, total_points) in enumerate(points_query, 1):
            user_data = serialized_users.get(user_id, {})
            user_data['rank'] = rank
            user_data['total_points'] = float(total_points) if total_points else 0
            results.append(user_data)
        
        # HELPER: simple_success_response - Lista de puntos
        return simple_success_response(results, 'User points list')
    
    if request.method == 'POST':
        if not is_admin and user_role != 'teacher':
            # HELPER: simple_error_response - Sin permisos para crear
            return simple_error_response('No autorizado para crear puntos de usuario, no es admin ni teacher', 403)
        
        # HELPER: validate_request_json - Validar datos de puntos
        data, error_response, status = validate_request_json(['user_id', 'points'])
        if error_response:
            return error_response, status
        
        user_exists = db.session.execute(
            db.select(Users).where(Users.user_id == data.get('user_id'))
        ).scalar()
        
        if not user_exists:
            # HELPER: simple_error_response - Usuario no encontrado
            return simple_error_response('Usuario no encontrado', 400)
        
        row = UserPoints(
            user_id=data.get('user_id'),
            points=data.get('points'),
            point_type=data.get('point_type', 'course'),
            event_description=data.get('event_description'),
            date=data.get('date')
        )
        db.session.add(row)
        db.session.commit()
        
        # HELPER: simple_success_response - Puntos creados
        return simple_success_response(row.serialize(), 'Puntos de usuario creados'), 201
    
    # HELPER: method_not_allowed_response - Método no permitido
    return method_not_allowed_response()

# GET/PUT/DELETE: Operaciones CRUD para punto específico
@api.route('/user-points/<int:point_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def user_point(point_id):
    # HELPER: validate_user_role - Verificar usuario autenticado
    user, error_response, status = validate_user_role()
    if error_response:
        return error_response, status

    row = db.session.execute(
        db.select(UserPoints).where(UserPoints.point_id == point_id)).scalar()

    if not row:
        # HELPER: simple_error_response - Punto no encontrado
        return simple_error_response('Registro de puntos no encontrado', 404)
    
    if request.method == 'GET':
        # HELPER: simple_success_response - Detalles del punto
        return simple_success_response(row.serialize(), f'Detalles del punto {point_id}')
    
    if request.method == 'PUT':
        if not user.get('is_admin') and user.get('role') != 'teacher':
            # HELPER: simple_error_response - Sin permisos para actualizar
            return simple_error_response('No eres un Admin ni Teacher, no puedes actualizar puntos', 403)

        # HELPER: validate_request_json - Validar datos de actualización
        data, error_response, status = validate_request_json()
        if error_response:
            return error_response, status

        if not data:
            # HELPER: simple_error_response - Datos requeridos
            return simple_error_response('Request body requerido para actualizar', 400)

        if 'user_id' in data:
            user_exists = db.session.execute(
                db.select(Users).where(Users.user_id == data['user_id'])
            ).scalar()
            if not user_exists:
                # HELPER: simple_error_response - Usuario no encontrado
                return simple_error_response('Usuario no encontrado', 400)
            
        row.points = data.get('points', row.points)
        row.point_type = data.get('point_type', row.point_type)
        row.event_description = data.get(
            'event_description', row.event_description)
        row.date = data.get('date', row.date)
        row.user_id = data.get('user_id', row.user_id)
        db.session.commit()
        
        # HELPER: simple_success_response - Punto actualizado
        return simple_success_response(row.serialize(), f'Punto {point_id} actualizado')
    
    if request.method == 'DELETE':
        if not user.get('is_admin') and user.get('role') != 'teacher':
            # HELPER: simple_error_response - Sin permisos para eliminar
            return simple_error_response('No eres un Admin ni Teacher, no puedes eliminar puntos', 403)
        
        db.session.delete(row)
        db.session.commit()
        
        # HELPER: simple_success_response - Punto eliminado
        return simple_success_response({}, f'Punto {point_id} eliminado')
    
    # HELPER: method_not_allowed_response - Método no permitido
    return method_not_allowed_response()

# GET/POST: Operaciones CRUD de progreso de usuario
@api.route('/userprogress', methods=['GET', 'POST'])
@jwt_required()
def user_progress():
    # HELPER: validate_user_role - Verificar usuario autenticado
    user, error_response, status = validate_user_role()
    if error_response:
        return error_response, status
    
    user_id = user.get('user_id')
    is_admin = user.get('is_admin', False)
    user_role = user.get('role')
    
    if request.method == 'GET':
        query = db.select(UserProgress)
        
        if not is_admin and user_role in ['student', 'demo']:
            query = query.where(UserProgress.user_id == user_id)
        
        rows = db.session.execute(query).scalars()
        results = [row.serialize() for row in rows]
        
        # HELPER: simple_success_response - Lista de progreso
        return simple_success_response(results, 'Listado de progreso de usuarios')
    
    if request.method == 'POST':
        if not is_admin and user_role != 'teacher':
            # HELPER: simple_error_response - Sin permisos para crear
            return simple_error_response('No autorizado para crear registros de progreso', 403)
        
        # HELPER: validate_request_json - Validar datos de progreso
        data, error_response, status = validate_request_json([
            'user_id', 'lesson_id', 'completed'
        ])
        if error_response:
            return error_response, status
        
        row = UserProgress(
            user_id=data.get('user_id'),
            lesson_id=data.get('lesson_id'),
            completed=data.get('completed', False),
            start_date=data.get('start_date'),
            completion_date=data.get('completion_date') if data.get('completed') else None
        )
        
        db.session.add(row)
        db.session.commit()
        
        # HELPER: simple_success_response - Progreso creado
        return simple_success_response(row.serialize(), 'Progreso de usuario creado'), 201
    
    # HELPER: method_not_allowed_response - Método no permitido
    return method_not_allowed_response()

# GET/PUT/DELETE: Operaciones CRUD para progreso específico
@api.route('/userprogress/<int:progress_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def user_progress_detail(progress_id):
    # HELPER: validate_user_role - Verificar usuario autenticado
    user, error_response, status = validate_user_role()
    if error_response:
        return error_response, status
    
    user_id = user.get('user_id')
    is_admin = user.get('is_admin', False)
    user_role = user.get('role')
    
    row = db.session.execute(
        db.select(UserProgress).where(UserProgress.progress_id == progress_id)
    ).scalar()

    if not row:
        # HELPER: simple_error_response - Progreso no encontrado
        return simple_error_response(f'Progreso {progress_id} no encontrado', 404)
    
    if not is_admin and user_role != 'teacher' and row.user_id != user_id:
        # HELPER: simple_error_response - Sin permisos para acceder
        return simple_error_response('No autorizado para acceder a este progreso', 403)

    if request.method == 'GET':
        # HELPER: simple_success_response - Detalles del progreso
        return simple_success_response(row.serialize(), f'Detalles del progreso {progress_id}')

    if request.method == 'PUT':
        if not is_admin and user_role != 'teacher':
            # HELPER: simple_error_response - Sin permisos para actualizar
            return simple_error_response('No autorizado para actualizar progreso', 403)
        
        # HELPER: validate_request_json - Validar datos de actualización
        data, error_response, status = validate_request_json()
        if error_response:
            return error_response, status
        
        if 'completed' in data:
            row.completed = bool(data['completed'])
            if data['completed'] and not row.completion_date:
                row.completion_date = datetime.now(timezone.utc)
            elif not data['completed']:
                row.completion_date = None
        
        if 'start_date' in data and data['start_date']:
            try:
                row.start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
            except ValueError:
                # HELPER: simple_error_response - Formato de fecha inválido
                return simple_error_response('Formato de fecha inválido para start_date', 400)
        
        db.session.commit()
        
        # HELPER: simple_success_response - Progreso actualizado
        return simple_success_response(row.serialize(), f'Progreso {progress_id} actualizado')

    if request.method == 'DELETE':
        if not is_admin:
            # HELPER: simple_error_response - Solo admin puede eliminar
            return simple_error_response('Solo administradores pueden eliminar progreso', 403)
        
        db.session.delete(row)
        db.session.commit()
        
        # HELPER: simple_success_response - Progreso eliminado
        return simple_success_response({}, f'Progreso {progress_id} eliminado')
    
    # HELPER: method_not_allowed_response - Método no permitido
    return method_not_allowed_response()

# GET/POST: Operaciones CRUD de logros
@api.route('/achievements', methods=['GET', 'POST'])
@jwt_required()
def achievements():
    # HELPER: validate_user_role - Verificar usuario autenticado
    user, error_response, status = validate_user_role()
    if error_response:
        return error_response, status
    
    is_admin = user.get('is_admin', False)
    
    if request.method == 'GET':
        rows = db.session.execute(
            db.select(Achievements)).scalars()
        results = [row.serialize() for row in rows]
        
        # HELPER: simple_success_response - Lista de logros
        return simple_success_response(results, 'Listado de logros')

    if request.method == 'POST':
        if not is_admin:
            # HELPER: simple_error_response - Solo admin puede crear
            return simple_error_response('Solo administradores pueden crear logros', 403)
        
        # HELPER: validate_request_json - Validar datos del logro
        data, error_response, status = validate_request_json([
            'name', 'description', 'required_points'
        ])
        if error_response:
            return error_response, status
        
        row = Achievements(
            name=data.get('name'),
            description=data.get('description'),
            required_points=data.get('required_points'),
            icon=data.get('icon'))
        
        db.session.add(row)
        db.session.commit()
        
        # HELPER: simple_success_response - Logro creado
        return simple_success_response(row.serialize(), 'Logro creado'), 201
    
    # HELPER: method_not_allowed_response - Método no permitido
    return method_not_allowed_response()

# GET/PUT/DELETE: Operaciones CRUD para logro específico
@api.route('/achievements/<int:achievement_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def achievement(achievement_id):
    # HELPER: validate_user_role - Verificar usuario autenticado
    user, error_response, status = validate_user_role()
    if error_response:
        return error_response, status
    
    is_admin = user.get('is_admin', False)
    
    row = db.session.execute(
        db.select(Achievements).where(Achievements.achievement_id == achievement_id)).scalar()
    
    if not row:
        # HELPER: simple_error_response - Logro no encontrado
        return simple_error_response('Logro no encontrado', 404)
    
    if request.method == 'GET':
        # HELPER: simple_success_response - Detalles del logro
        return simple_success_response(row.serialize(), f'Detalles del logro {achievement_id}')
    
    if request.method == 'PUT':
        if not is_admin:
            # HELPER: simple_error_response - Solo admin puede actualizar
            return simple_error_response('Solo administradores pueden actualizar logros', 403)
        
        # HELPER: validate_request_json - Validar datos de actualización
        data, error_response, status = validate_request_json()
        if error_response:
            return error_response, status
        
        row.name = data.get('name', row.name)
        row.description = data.get('description', row.description)
        row.required_points = data.get('required_points', row.required_points)
        row.icon = data.get('icon', row.icon)
        
        db.session.commit()
        
        # HELPER: simple_success_response - Logro actualizado
        return simple_success_response(row.serialize(), f'Logro {achievement_id} actualizado')
    
    if request.method == 'DELETE':
        if not is_admin:
            # HELPER: simple_error_response - Solo admin puede eliminar
            return simple_error_response('Solo administradores pueden eliminar logros', 403)
        
        db.session.delete(row)
        db.session.commit()
        
        # HELPER: simple_success_response - Logro eliminado
        return simple_success_response({}, f'Logro {achievement_id} eliminado')
    
    # HELPER: method_not_allowed_response - Método no permitido
    return method_not_allowed_response()

# GET/POST: Operaciones CRUD de logros de usuario
@api.route('/user-achievements', methods=['GET', 'POST'])
@jwt_required()
def user_achievements():
    # HELPER: validate_user_role - Verificar usuario autenticado
    user, error_response, status = validate_user_role()
    if error_response:
        return error_response, status
    
    is_admin = user.get('is_admin', False)
    user_role = user.get('role')
    
    if request.method == 'GET':
        rows = db.session.execute(db.select(UserAchievements)).scalars()
        results = [row.serialize() for row in rows]
        
        # HELPER: simple_success_response - Lista de logros de usuario
        return simple_success_response(results, 'Listado de logros obtenidos por usuarios')

    if request.method == 'POST':
        if not is_admin and user_role != 'teacher':
            # HELPER: simple_error_response - Sin permisos para asignar
            return simple_error_response('No autorizado para asignar logros', 403)
        
        # HELPER: validate_request_json - Validar datos de logro de usuario
        data, error_response, status = validate_request_json([
            'user_id', 'achievement_id'
        ])
        if error_response:
            return error_response, status
        
        required_fields = ['user_id', 'achievement_id']
        missing_fields = [
            field for field in required_fields if field not in data]
        if missing_fields:
            # HELPER: simple_error_response - Campos faltantes
            return simple_error_response('Faltan campos requeridos', 400)

        user_exists = db.session.execute(
            db.select(Users).where(Users.user_id == data.get('user_id'))).scalar()
        if not user_exists:
            # HELPER: simple_error_response - Usuario no encontrado
            return simple_error_response('Usuario no encontrado', 400)

        achievement_exists = db.session.execute(
            db.select(Achievements).where(
                Achievements.achievement_id == data.get('achievement_id'))).scalar()
        if not achievement_exists:
            # HELPER: simple_error_response - Logro no encontrado
            return simple_error_response('Logro no encontrado', 400)

        existing = db.session.execute(
            db.select(UserAchievements).where(
                UserAchievements.user_id == data.get('user_id'),
                UserAchievements.achievement_id == data.get('achievement_id'))).scalar()
        if existing:
            # HELPER: simple_error_response - Ya tiene el logro
            return simple_error_response('El usuario ya tiene este logro', 409)

        obtained_date = datetime.now(timezone.utc)
        if data.get('obtained_date'):
            try:
                obtained_date = datetime.fromisoformat(
                    data.get('obtained_date').replace('Z', '+00:00'))
            except ValueError:
                # HELPER: simple_error_response - Formato de fecha inválido
                return simple_error_response('Formato de fecha inválido', 400)

        row = UserAchievements(
            user_id=data.get('user_id'),
            achievement_id=data.get('achievement_id'),
            obtained_date=obtained_date)
        
        db.session.add(row)
        db.session.commit()
        
        # HELPER: simple_success_response - Logro asignado
        return simple_success_response(row.serialize(), 'Logro asignado al usuario'), 201
    
    # HELPER: method_not_allowed_response - Método no permitido
    return method_not_allowed_response()

# GET/PUT/DELETE: Operaciones CRUD para logro de usuario específico
@api.route('/user-achievements/<int:user_achievement_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def user_achievement(user_achievement_id):
    # HELPER: validate_user_role - Verificar usuario autenticado
    user, error_response, status = validate_user_role()
    if error_response:
        return error_response, status
    
    is_admin = user.get('is_admin', False)
    user_role = user.get('role')
    current_user_id = user.get('user_id')

    row = db.session.execute(
        db.select(UserAchievements).where(
            UserAchievements.user_achievement_id == user_achievement_id)).scalar()
    
    if not row:
        # HELPER: simple_error_response - Logro de usuario no encontrado
        return simple_error_response('Logro de usuario no encontrado', 404)

    if request.method == 'GET':
        if not is_admin and user_role != 'teacher' and row.user_id != current_user_id:
            # HELPER: simple_error_response - Sin permisos para ver
            return simple_error_response('No autorizado para ver este logro', 403)
        
        # HELPER: simple_success_response - Detalles del logro de usuario
        return simple_success_response(row.serialize(), f'Detalles del logro de usuario {user_achievement_id}')

    if request.method == 'PUT':
        if not is_admin and user_role != 'teacher':
            # HELPER: simple_error_response - Sin permisos para actualizar
            return simple_error_response('No autorizado para actualizar logros', 403)
        
        # HELPER: validate_request_json - Validar datos de actualización
        data, error_response, status = validate_request_json()
        if error_response:
            return error_response, status
        
        if 'obtained_date' in data:
            try:
                row.obtained_date = datetime.fromisoformat(data['obtained_date'].replace('Z', '+00:00'))
            except ValueError:
                # HELPER: simple_error_response - Formato de fecha inválido
                return simple_error_response('Formato de fecha inválido', 400)
        
        db.session.commit()
        
        # HELPER: simple_success_response - Logro de usuario actualizado
        return simple_success_response(row.serialize(), f'Logro de usuario {user_achievement_id} actualizado')

    if request.method == 'DELETE':
        if not is_admin:
            # HELPER: simple_error_response - Solo admin puede eliminar
            return simple_error_response('Solo administradores pueden eliminar logros', 403)

        db.session.delete(row)
        db.session.commit()
        
        # HELPER: simple_success_response - Logro de usuario eliminado
        return simple_success_response({}, f'Logro de usuario {user_achievement_id} eliminado')
    
    # HELPER: method_not_allowed_response - Método no permitido
    return method_not_allowed_response()

# GET/POST: Operaciones CRUD de recursos multimedia
@api.route('/multimedia-resources', methods=['GET', 'POST'])
@jwt_required()
def multimedia_resources():
    # HELPER: validate_user_role - Verificar usuario autenticado
    user, error_response, status = validate_user_role()
    if error_response:
        return error_response, status
    
    is_admin = user.get('is_admin', False)
    user_role = user.get('role')
    
    if request.method == 'GET':
        rows = db.session.execute(db.select(MultimediaResources)).scalars()
        results = [row.serialize() for row in rows]
        
        # HELPER: simple_success_response - Lista de recursos multimedia
        return simple_success_response(results, 'Listado de recursos multimedia')
    
    if request.method == 'POST':
        if not is_admin and user_role != 'teacher':
            # HELPER: simple_error_response - Sin permisos para crear
            return simple_error_response('No autorizado para crear recursos multimedia', 403)
        
        # HELPER: validate_request_json - Validar datos del recurso
        data, error_response, status = validate_request_json([
            'type', 'url', 'order', 'lesson_id'
        ])
        if error_response:
            return error_response, status
        
        if not data:
            # HELPER: simple_error_response - Datos requeridos
            return simple_error_response('Request body requerido', 400)
        
        required_fields = ['type', 'url', 'order', 'lesson_id']
        missing_fields = [f for f in required_fields if f not in data]
        if missing_fields:
            # HELPER: simple_error_response - Campos faltantes
            return simple_error_response('Faltan campos requeridos', 400)
        
        allowed_types = ['video', 'image', 'gif', 'animation', 'document']
        if data.get('type') not in allowed_types:
            # HELPER: simple_error_response - Tipo inválido
            return simple_error_response('Tipo de recurso inválido', 400)
        
        if not data.get('url').startswith(('http://', 'https://')):
            # HELPER: simple_error_response - URL inválida
            return simple_error_response('URL inválida', 400)
        
        lesson = db.session.execute(
            db.select(Lessons).where(Lessons.lesson_id == data.get('lesson_id'))).scalar()
        if not lesson:
            # HELPER: simple_error_response - Lección no encontrada
            return simple_error_response('Lección no encontrada', 400)

        existing = db.session.execute(
            db.select(MultimediaResources).where(
                MultimediaResources.lesson_id == data.get('lesson_id'),
                MultimediaResources.order == data.get('order'))).scalar()
        if existing:
            # HELPER: simple_error_response - Orden duplicado
            return simple_error_response('Ya existe un recurso con este orden', 409)
        
        row = MultimediaResources(
            resource_type=data.get('type'),
            url=data.get('url'),
            duration_seconds=data.get('duration_seconds'),
            description=data.get('description'),
            order=data.get('order'),
            lesson_id=data.get('lesson_id')
        )
        db.session.add(row)
        db.session.commit()
        
        # HELPER: simple_success_response - Recurso creado
        return simple_success_response(row.serialize(), 'Recurso multimedia creado'), 201
    
    # HELPER: method_not_allowed_response - Método no permitido
    return method_not_allowed_response()

# GET/PUT/DELETE: Operaciones CRUD para recurso multimedia específico
@api.route('/multimedia-resources/<int:resource_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def multimedia_resource(resource_id):
    # HELPER: validate_user_role - Verificar usuario autenticado
    user, error_response, status = validate_user_role()
    if error_response:
        return error_response, status
    
    is_admin = user.get('is_admin', False)
    user_role = user.get('role')

    row = db.session.execute(
        db.select(MultimediaResources).where(
            MultimediaResources.resource_id == resource_id)).scalar()
    
    if not row:
        # HELPER: simple_error_response - Recurso no encontrado
        return simple_error_response('Recurso multimedia no encontrado', 404)

    if request.method == 'GET':
        # HELPER: simple_success_response - Detalles del recurso
        return simple_success_response(row.serialize(), 'Detalle del recurso multimedia')

    if request.method == 'PUT':
        if not is_admin and user_role != 'teacher':
            # HELPER: simple_error_response - Sin permisos para actualizar
            return simple_error_response('No autorizado para actualizar recursos', 403)

        # HELPER: validate_request_json - Validar datos de actualización
        data, error_response, status = validate_request_json()
        if error_response:
            return error_response, status
        
        if 'type' in data:
            allowed_types = ['video', 'image', 'gif', 'animation', 'document']
            if data['type'] not in allowed_types:
                # HELPER: simple_error_response - Tipo inválido
                return simple_error_response('Tipo de recurso inválido', 400)
            row.resource_type = data['type']
        
        if 'url' in data:
            if not data['url'].startswith(('http://', 'https://')):
                # HELPER: simple_error_response - URL inválida
                return simple_error_response('URL inválida', 400)
            row.url = data['url']
        
        if 'order' in data:
            row.order = data['order']
        
        if 'description' in data:
            row.description = data['description']
        
        if 'duration_seconds' in data:
            row.duration_seconds = data['duration_seconds']
        
        db.session.commit()
        
        # HELPER: simple_success_response - Recurso actualizado
        return simple_success_response(row.serialize(), 'Recurso multimedia actualizado')

    if request.method == 'DELETE':
        if not is_admin:
            # HELPER: simple_error_response - Solo admin puede eliminar
            return simple_error_response('Solo administradores pueden eliminar recursos', 403)

        db.session.delete(row)
        db.session.commit()
        
        # HELPER: simple_success_response - Recurso eliminado
        return simple_success_response({}, 'Recurso multimedia eliminado')
    
    # HELPER: method_not_allowed_response - Método no permitido
    return method_not_allowed_response()

# POST: Webhook de Stripe para procesar pagos
@api.route('/stripe-webhook', methods=['POST'])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = current_app.config.get('STRIPE_WEBHOOK_SECRET', '')
    
    if not webhook_secret:
        try:
            event = json.loads(payload)
            event_type = event.get('type', 'unknown')
        except json.JSONDecodeError:
            # HELPER: simple_error_response - JSON inválido
            return simple_error_response('Invalid JSON payload', 400)
    else:
        verification_result = stripe_service.verify_webhook_signature(payload, sig_header)
        
        if not verification_result['success']:
            # HELPER: simple_error_response - Firma inválida
            return simple_error_response(
                verification_result.get('error', 'Invalid signature'),
                400
            )
        
        event = verification_result['event']
        event_type = verification_result['type']
    
    try:
        if event_type == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            stripe_payment_id = payment_intent['id']
            
            purchase = db.session.execute(
                db.select(Purchases).where(
                    Purchases.stripe_payment_intent_id == stripe_payment_id
                )
            ).scalar()
            
            if purchase:
                if purchase.status != 'pending':
                    pass
                
                purchase.status = 'paid'
                purchase.start_date = datetime.now(timezone.utc)
                
                user = db.session.execute(
                    db.select(Users).where(Users.user_id == purchase.user_id)
                ).scalar()
                
                if user:
                    course = db.session.execute(
                        db.select(Courses).where(Courses.course_id == purchase.course_id)
                    ).scalar()
                    
                    if course and course.points > 0:
                        existing_points = db.session.execute(
                            db.select(UserPoints).where(
                                UserPoints.user_id == purchase.user_id,
                                UserPoints.event_description.like(f"%Compra {purchase.purchase_id}%")
                            )
                        ).scalar()
                        
                        if not existing_points:
                            user_point = UserPoints(
                                user_id=purchase.user_id,
                                points=course.points,
                                point_type='course_purchase',
                                event_description=f"Compra {purchase.purchase_id} del curso: {course.title}",
                                date=datetime.now(timezone.utc)
                            )
                            db.session.add(user_point)
                            
                            user.current_points = (user.current_points or 0) + course.points
                
                db.session.commit()
                
            else:
                metadata = payment_intent.get('metadata', {})
                purchase_id_from_meta = metadata.get('purchase_id')
                
                if purchase_id_from_meta:
                    purchase = db.session.execute(
                        db.select(Purchases).where(Purchases.purchase_id == int(purchase_id_from_meta))
                    ).scalar()
                    
                    if purchase:
                        purchase.status = 'paid'
                        purchase.start_date = datetime.now(timezone.utc)
                        purchase.stripe_payment_intent_id = stripe_payment_id
                        db.session.commit()
        
        elif event_type == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            stripe_payment_id = payment_intent['id']
            
            purchase = db.session.execute(
                db.select(Purchases).where(
                    Purchases.stripe_payment_intent_id == stripe_payment_id
                )
            ).scalar()
            
            if purchase:
                purchase.status = 'cancelled'
                db.session.commit()
        
        elif event_type == 'checkout.session.completed':
            pass
        
        elif event_type == 'charge.refunded':
            pass
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        
        # HELPER: simple_error_response - Error al procesar webhook
        return simple_error_response(str(e), 200)
    
    # HELPER: simple_success_response - Webhook procesado
    return simple_success_response({
        'event_type': event_type,
        'processed': True,
        'timestamp': datetime.now(timezone.utc).isoformat()
    }, 'Webhook procesado exitosamente')