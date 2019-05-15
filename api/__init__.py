import os
from flask import Flask
from mongoengine import connect


def create_app():
    app = Flask(__name__)
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

    connect(host=os.getenv('MONGODB_URI'))
    return app
