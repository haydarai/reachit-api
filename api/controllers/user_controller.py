from api.models.user_model import User
from flask_restful import Resource, reqparse
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required, get_jwt_identity)
import app
import json


class UserController(Resource):
    def post(self):
        parser = reqparse.RequestParser()

        parser.add_argument('email', required=True, help='Email is required')
        parser.add_argument('name', required=True, help='Name is required.')
        parser.add_argument('password', required=True,
                            help='Password is required.')

        data = parser.parse_args()
        try:
            original_password = data.password
            data.password = app.bcrypt.generate_password_hash(
                data.password).decode('utf-8')
            password = app.bcrypt.check_password_hash(
                data.password, original_password)
        except:
            return {'message': 'Password must be not empty.'}, 403

        user = User.objects(pk=data.email).first()
        if user:
            return {'message': 'User exists.'}, 403
        user = User(email=data.email, name=data.name, password=data.password)
        user.save()
        user = json.loads(user.to_json())
        return {'message': 'User created.'}, 201


class UserLoginController(Resource):
    def post(self):
        parser = reqparse.RequestParser()

        parser.add_argument('email', required=True, help='Email is required')
        parser.add_argument('password', required=True,
                            help='Password is required.')

        data = parser.parse_args()

        user = User.objects(pk=data.email).first()
        if not user:
            return {'message': 'User does not exist.'}, 403

        if not app.bcrypt.check_password_hash(user.password, data.password):
            return {'message': 'Password does not match.'}, 401

        user = json.loads(user.to_json())
        access_token = create_access_token(identity=user)
        return {'access_token': access_token}


class UserProfileController(Resource):
    @jwt_required
    def get(self):
        user = get_jwt_identity()
        return user
