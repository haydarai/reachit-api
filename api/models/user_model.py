import mongoengine as db
import mongoengine_goodjson as gj


class User(gj.Document):
    email = db.StringField(required=True, primary_key=True)
    name = db.StringField(required=True, max_length=100)
    password = db.StringField(required=True)
    meta = {'collection': 'users'}
