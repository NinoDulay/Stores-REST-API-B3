from flask.views import MethodView
from flask_smorest import Blueprint, abort
from schemas import UserSchema

from models import UserModel

from sqlalchemy.exc import SQLAlchemyError

from db import db
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token, get_jwt, jwt_required, create_refresh_token

from blocklist import BLOCKLIST

blp = Blueprint("Users", __name__, description="Operation on users.")


'''
'/register'  - POST   (accepts username and password)

'login' - POST        (Get JWT)

'/user/<id>' - GET    (get user)      - TEMPORARY (for testing only)
'/user/<id>' - DELETE (delete user)   - TEMPORARY (for testing only)
'''

@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    def post(self, request_body):
        # Check if the user exists
        user = UserModel.query.filter(UserModel.username == request_body["username"]).first()

        # Check if password correct and user exists
        if user: # Does the user exist?
            # Check password
            if pbkdf2_sha256.verify(request_body["password"], user.password):
                
                access_token = create_access_token(identity=str(user.id), fresh=True)

                refresh_token = create_refresh_token(identity=str(user.id))

                return {
                    "access_token": access_token, 
                    "refresh_token": refresh_token
                }, 200
        else:
            abort(401, message="User does not exist.")

@blp.route("/refresh")
class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        # Current user
        current_user = get_jwt().get("sub")

        # Create non-fresh
        new_token = create_access_token(identity=str(current_user), fresh=False)

        return {"access_token": new_token}


@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        # Get JWT
        jwt = get_jwt()

        jti = jwt["jti"]

        BLOCKLIST.add(jti)
        return {"message": "Successfully logged out."}



@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserSchema)
    def post(self, request_body):
        # Ensure user does not exist
        if UserModel.query.filter(
            UserModel.username == request_body["username"]
        ).first():
            abort(409, message="A user with that username already exists.")

        # Create a new user model
        new_user = UserModel(
            username=request_body["username"],
            password=pbkdf2_sha256.hash(request_body["password"])
        )

        db.session.add(new_user)
        db.session.commit()

        return {"message": "User created successfully."}, 201


@blp.route("/user/<string:user_id>")
class User(MethodView):
    @blp.response(200, UserSchema)
    def get(self, user_id):
        return UserModel.query.get_or_404(user_id)

    def delete(self, user_id):
        user_to_delete = UserModel.query.get_or_404(user_id)
        db.session.delete(user_to_delete)
        db.session.commit()

        return {"message": "User Deleted"}, 200
    