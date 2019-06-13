from api.controllers.promotion_controller import *
from api.controllers.transaction_controller import *
from api.controllers.user_controller import *
from api import create_app
from flask_restful import Api
from flask_bcrypt import Bcrypt
from flask_jwt_extended import (JWTManager)
from neo4j import GraphDatabase
from dotenv import load_dotenv
load_dotenv()


app = create_app()
api = Api(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
neo4j_driver = GraphDatabase.driver()

api.add_resource(UserController, '/users')
api.add_resource(UserProfileController, '/users/me')
api.add_resource(UserLoginController, '/users/login')
api.add_resource(TransactionController, '/users/me/transactions')
api.add_resource(TransactionDetailController,
                '/users/me/transactions/<string:transaction_id>')
api.add_resource(PromotionController, '/promotions')
api.add_resource(PromotionDetailController,
                '/promotions/<string:promotion_id>')
