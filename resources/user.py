from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_refresh_token_required,
    get_jwt_identity,
    jwt_required,
    get_raw_jwt,
)
from flask_restful import Resource, reqparse
from models.user import UserModel
from werkzeug.security import safe_str_cmp

from blacklist import BLACKLIST

REQUIRED_ERROR = "This field '{}' is required!"
USER_ALREADY_EXIST = "The user with name '{}' already exists"
ERROR_INSERTING = "DB error occurred while db insertion"
CREATED_SUCCESSFULLY = "User created successfully"
USER_NOT_FOUND = "The user is not found"
USER_DELETED = "The user is deleted"
INVALID_CREDENTIALS = "Invalid credentials"
USER_LOGGED_OUT = "User <id={user_id}> successfully logged out"

_user_parser = reqparse.RequestParser()
_user_parser.add_argument(
    "username", type=str, required=True, help=REQUIRED_ERROR.format("username")
)
_user_parser.add_argument(
    "password", type=str, required=True, help=REQUIRED_ERROR.format("password")
)


class UserRegister(Resource):
    def post(self):
        data = _user_parser.parse_args()
        username = data["username"]
        if UserModel.find_by_username(username):
            return {"message": USER_ALREADY_EXIST.format(username)}, 409

        user = UserModel(**data)
        user.save_to_db()

        return {"message": CREATED_SUCCESSFULLY}, 201


class User(Resource):
    @classmethod
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if user:
            return user.json
        return {"message": USER_NOT_FOUND}, 404

    @classmethod
    def delete(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if user:
            return user.delete_from_db()
        return {"message": USER_NOT_FOUND}, 404


class UserLogin(Resource):
    @classmethod
    def post(cls):
        data = _user_parser.parse_args()
        user = UserModel.find_by_username(data["username"])

        if user and safe_str_cmp(user.password, data["password"]):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(user.id)
            return {"access_token": access_token, "refresh_token": refresh_token}, 200
        return {"message": INVALID_CREDENTIALS}, 401


class UserLogout(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()["jti"]  # jti unique identifier of jwt
        user_id = get_jwt_identity()
        BLACKLIST.add(jti)
        return {"message": USER_LOGGED_OUT.format(user_id)}


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}, 200
