from flask import Blueprint, jsonify, request
from src.constants.http_status_codes import  HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT
import validators
from src.database import User, db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity


auth = Blueprint("auth", __name__, url_prefix="/auth")

# user registration route
@auth.post("/register")
def register():
    name = request.json["name"]
    email = request.json["email"]
    password = request.json["password"]

    # validating the name 
    if len(name) < 3:
        return jsonify({'error': "name is too short"}), HTTP_400_BAD_REQUEST
    
    if not name.isalnum() or " " in name:
        return jsonify({"error": "name should not contain numbers or symbols"}), HTTP_400_BAD_REQUEST
    
    # validate the user email
    if not validators.email(email):
        return jsonify({"error": "email is not valid"})
    
    # check if the user email is not already registered in the database
    if User.query.filter_by(email=email).first():
        return jsonify({'error': "email already exist"}), HTTP_409_CONFLICT
    # check if the username is not already registered in the database
    if User.query.filter_by(name=name).first():
        return jsonify({"error": 'name already exist'})
    
    # save the contents of the user into the user table
    password_hash=generate_password_hash(password)

    user=User(name=name, email=email, password_hash=password_hash)
    db.session.add(user)
    db.session.commit()

    return jsonify({
        'message': "User created",
        'user':{
            'name':name, 'email': email
        }
    }), HTTP_201_CREATED

# user login route
@auth.post("/login")
def login():
    email = request.json.get("email")
    password = request.json.get("password")

    # get the user by email
    user=User.query.filter_by(email=email).first()

    if user:
        check_hashed_password=check_password_hash(user.password_hash, password)

        if check_hashed_password:
            # create jwt access tokens and refresh token to authenticate and authorise users
            refresh=create_refresh_token(identity=str(user.id))
            access=create_access_token(identity=str(user.id))

            return jsonify({
                'user':{
                    'refresh': refresh,
                    'access': access,
                    'name': user.name,
                    'email': user.email,
                    'id': user.id
                }
            }), HTTP_200_OK
    return jsonify({'error': 'wrong username or password'}), HTTP_400_BAD_REQUEST

# get user profile after login
@auth.get("/profile")
@jwt_required()
def profile():
    user_id = get_jwt_identity()

    user=User.query.filter_by(id=user_id).first()

    return jsonify({
        'user':{
            'name': user.name,
            'email': user.email
        }
    }), HTTP_200_OK

# create user refresh token
@auth.get("/token/refresh")
@jwt_required(refresh=True)
def refresh_token():
    user_id=get_jwt_identity()
    access=create_access_token(identity=str(user_id))

    return jsonify({
        'access': access
    }), HTTP_200_OK