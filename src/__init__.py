from flask import Flask, jsonify
import os
from src.auth import auth
from src.todos import todos
from src.database import db
from flask_jwt_extended import JWTManager
from src.constants.http_status_codes import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_503_SERVICE_UNAVAILABLE

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        app.config.from_mapping(
            SECRET_KEY=os.environ.get("SECRET_KEY"),
            SQLALCHEMY_DATABASE_URI=os.environ.get('SQLALCHEMY_DATABASE_URI'),
            JWT_SECRET_KEY=os.environ.get('JWT_SECRET_KEY')
        )
    else:
        app.config.from_mapping(test_config)
    
    # initialise the database
    db.app=app
    db.init_app(app)
    
    # initialise jwt
    JWTManager(app)
    # configure blueprints
    app.register_blueprint(auth)
    app.register_blueprint(todos)

    # exception handling
    @app.errorhandler(HTTP_404_NOT_FOUND)
    def handle_file_not_found(error):
        return jsonify({'error': f"{HTTP_404_NOT_FOUND} File not found!"}), HTTP_404_NOT_FOUND
    
    @app.errorhandler(HTTP_500_INTERNAL_SERVER_ERROR)
    def handle_internalServer_error(error):
        return jsonify({'error': "Something went wrong!"}), HTTP_500_INTERNAL_SERVER_ERROR
    
    @app.errorhandler(HTTP_503_SERVICE_UNAVAILABLE)
    def handle_connection_error(error):
        return jsonify({'error': "Service is currently unavailable. Our team is working on it!"}), HTTP_503_SERVICE_UNAVAILABLE

    return app