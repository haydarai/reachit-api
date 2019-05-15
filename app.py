from flask_restful import Api
from flask_bcrypt import Bcrypt
from flask_jwt_extended import (JWTManager)
from dotenv import load_dotenv
load_dotenv()

from api import create_app
from api.controllers.user_controller import *

app = create_app()
api = Api(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

api.add_resource(UserController, '/users')
api.add_resource(UserProfileController, '/users/me')
api.add_resource(UserLoginController, '/users/login')
