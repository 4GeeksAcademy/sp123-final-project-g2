from flask import request, jsonify, Blueprint
from datetime import datetime, timedelta, timezone
from api.models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
import jwt

api_user = Blueprint('apiUser', __name__)

# Allow CORS requests to this API
CORS(api_user)
SECRET_KEY = "super-secret-key"


@api_user.route('/register', methods=['POST'])
def crear_perfil():
    body = request.get_json()
    email = body.get('email')
    password = body.get('password')
    if not email or not password:
        return jsonify({"msg": "Falta correo o contraseña"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "El usuario ya existe"}), 400
    hashed_password = generate_password_hash(password)

    print(body)

    nuevo_perfil = User(
        email=email,
        password=hashed_password,
        name=body.get("name"),
        photo=body.get("photo"),
        bio=body.get("bio"),
        phone=body.get("phone"),
        age=body.get("age"),
        city=body.get("city"),
        gender=body.get("gender"),
        twitter=body.get("twitter"),
        facebook=body.get("facebook"),
        instagram=body.get("instagram"),
    )

    db.session.add(nuevo_perfil)
    db.session.commit()

    return jsonify({
        "msg": "Perfil creado correctamente", "perfil": nuevo_perfil.serialize()
    }), 201


@api_user.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({"msg": "Falta correo o contraseña"}), 400
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"msg": "Usuario o contraseña incorrectos"}), 401
    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.now(timezone.utc) + timedelta(minutes=15)
    }, SECRET_KEY, algorithm="HS256")
    return jsonify({"token": token, "user": user.serialize()})


@api_user.route('/<int:user_id>/perfil', methods=['GET'])
def get_perfil(user_id):
    varPerfil = User.query.filter_by(user_id=user_id).first()
    if varPerfil is None:
        return jsonify({"msg": f"El usuario con el ID {user_id} no existe"}), 404

    response_body = {
        "Perfil": varPerfil.serialize()
    }
    return jsonify(response_body), 200


@api_user.route('/<int:user_id>/perfil', methods=['PUT'])
def editar_perfil(user_id):
    varUser = User.query.get(user_id)
    if varUser is None:
        return jsonify({'msg': f'El usuario con ID {user_id} no existe'}), 404
    varPerfil = User.query.filter_by(user_id=user_id).first()
    if varPerfil is None:
        return jsonify({'msg': f'El usuario con ID {user_id} no tiene perfil creado'}), 404
    body = request.get_json(silent=True)
    if body is None:
        return jsonify({'msg': 'No se encuentra body, no hay datos que actualizar'}), 400

    if "nombre" in body:
        if body["nombre"].strip() == "":
            return jsonify({'msg': 'El nombre no puede estar vacío'}), 400
        varPerfil.nombre = body["nombre"]
    if "foto" in body:
        varPerfil.foto = body["foto"]
    if "presentacion" in body:
        varPerfil.presentacion = body["presentacion"]
    if "telefono" in body:
        varPerfil.telefono = body["telefono"]
    if "edad" in body:
        varPerfil.edad = body["edad"]
    if "ciudad" in body:
        varPerfil.ciudad = body["ciudad"]
    if "genero" in body:
        varPerfil.genero = body["genero"]
    if "twitter" in body:
        varPerfil.twitter = body["twitter"]
    if "facebook" in body:
        varPerfil.facebook = body["facebook"]
    if "instagram" in body:
        varPerfil.instagram = body["instagram"]

    db.session.commit()

    return jsonify({
        'msg': 'Perfil actualizado correctamente', 'perfil': varPerfil.serialize()
    }), 200


@api_user.route('/Saluda', methods=['POST', 'GET'])
def handle_hello():

    response_body = {
        "message": "Este ya es el endpoint de Los usuarios Osea de cada user de la tabla"
    }

    return jsonify(response_body), 200
