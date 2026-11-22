from flask import Flask, request, jsonify
from db import db
import uuid
import requests

from flask_smorest import Api
from blocklist import BLOCKLIST

from resources.items import blp as ItemBlueprint
from resources.stores import blp as StoreBlueprint
from resources.tag import blp as TagBlueprint
from resources.user import blp as UserBlueprint

from models import UserModel, TagModel, StoreModel, ItemModel, ItemTags

from flask_jwt_extended import JWTManager 

from flask_migrate import Migrate

import os

def create_app(db_url=None):
    app = Flask(__name__)

    # SETTINGS
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Stores REST API B3 - AltSys Academy"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.2.1"
    app.config["OPENAPI_URL_PREFIX"] = "/"

    # DOCUMENTATION
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/docs"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

    # SETUP DATABASE
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL") or "sqlite:///data.db"
    # Connect our flask_sqlalchemy to flask_smorest
    db.init_app(app)

    migrate = Migrate(app, db)

    # CREATE ALL TABLES FROM THE MODELS
    # with app.app_context():
    #     db.create_all()

    # Register the blueprints to the API
    api = Api(app)
    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(TagBlueprint)
    api.register_blueprint(UserBlueprint)


    # Setup a signature for the JWT Manager
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY_RENDER")

    # Setup the JWT Manager
    jwt = JWTManager(app)

    # This will always run when we receive a JWT
    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        if jwt_payload["jti"] in BLOCKLIST:
            return True
        else:
            return False

    # Custom error message if the token that has been given is already in the blocklist
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {
                    "description": "The token has been revoked.",
                    "error": "token_revoked"
                }
            ), 401
        )

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({"message": "The token has expired.", "error": "token_expired"}),
            401,
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify(
                {"message": "Signature verification failed.", "error": "invalid_token"}
            ),
            401,
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify(
                {
                    "description": "Request does not contain an access token.",
                    "error": "authorization_required",
                }
            ),
            401,
        )

    return app

# Execute the API Server
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)