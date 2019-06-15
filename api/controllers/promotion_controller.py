import os
from io import BytesIO
from api.models.promotion_model import Promotion
from flask import request
from flask_restful import Resource, reqparse
from flask_jwt_extended import (
    jwt_required, get_jwt_identity
)
from datetime import datetime
import json
from werkzeug.datastructures import FileStorage
import boto
from boto.s3.connection import S3Connection
from boto.s3.key import Key as S3Key
from datetime import timezone, datetime
# from app import neo4j_driver

ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png']
FILE_CONTENT_TYPES = {  # these will be used to set the content type of S3 object. It is binary by default.
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png'
}


class FileStorageArgument(reqparse.Argument):
    def convert(self, value, op):
        if self.type is FileStorage:
            return value

        super(FileStorageArgument, self).convert(*args, **kwargs)


def upload_s3(file, key_name, content_type, bucket_name):
    bucket = boto.connect_s3(aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                             aws_secret_access_key=os.getenv(
        'AWS_SECRET_ACCESS_KEY'),
        host=os.getenv('AWS_S3_HOST')
    ).get_bucket(bucket_name)
    obj = S3Key(bucket)
    obj.name = key_name
    obj.content_type = content_type
    obj.set_contents_from_string(file.getvalue())
    obj.set_acl('public-read')

    # close stringio object
    file.close()

    return obj.generate_url(expires_in=0, query_auth=False)


class PromotionController(Resource):
    @jwt_required
    def get(self):
        neo4j_uri = os.getenv('NEO4J_URL')
        neo4j_user = os.getenv('NEO4J_USER')
        neo4j_password = os.getenv('NEO4J_PASSWORD')
        neo4j_driver = GraphDatabase.driver(
        neo4j_uri, auth=(neo4j_user, neo4j_password))
        
        user = get_jwt_identity()
        with neo4j_driver.session() as session:
            types = []
            result = session.run("""
                MATCH (u:User)-[getPromotion]-(t:Type) WHERE u.email = {email} RETURN t.typeName AS type ORDER BY u.userName
            """, email=user['id'])
            for row in result:
                types.append(row['type'])

            current_time = datetime.utcnow()
            promotions = Promotion.objects(
                product_type__in=types, start_valid_date__lte=current_time, end_valid_date__gte=current_time)
            promotions = json.loads(promotions.to_json())
            return {'promotions': promotions}

    @jwt_required
    def post(self):
        user = get_jwt_identity()
        if user['user_type'] != 'merchant':
            return {'message': 'Only merchant can create promotion.'}, 400

        parser = reqparse.RequestParser()

        parser.add_argument('title', required=True, help='Title is required')
        parser.add_argument('description')
        parser.add_argument('image', type=FileStorage, location='files')
        parser.add_argument('start_valid_date')
        parser.add_argument('end_valid_date')

        data = parser.parse_args()
        try:
            data['start_valid_date'] = datetime.strptime(
                data['start_valid_date'], '%Y-%m-%d %H:%M:%S')
        except:
            data['start_valid_date'] = None

        try:
            data['end_valid_date'] = datetime.strptime(
                data['end_valid_date'], '%Y-%m-%d %H:%M:%S')
        except:
            default_end_valid_date = datetime.utcnow()
            default_end_valid_date = default_end_valid_date.replace(year=3019)
            data['end_valid_date'] = default_end_valid_date

        if data.image:
            image = data['image']

            file_name = str(
                int(datetime.now(tz=timezone.utc).timestamp() * 1000))
            extension = image.filename.rsplit('.', 1)[1].lower()
            if '.' in image.filename and not extension in ALLOWED_EXTENSIONS:
                return {'message': 'File extension is not one of our supported types.'}, 400
            image_file = BytesIO()
            image.save(image_file)

            key_name = '{0}.{1}'.format(file_name, extension)
            content_type = FILE_CONTENT_TYPES[extension]
            bucket_name = os.getenv('AWS_S3_BUCKET_NAME')
            data['image'] = upload_s3(image_file, key_name,
                                      content_type, bucket_name)
        else:
            data['image'] = ''

        promotion = Promotion(creator=user['id'], title=data.title, description=data.description, image=data.image,
                              start_valid_date=data.start_valid_date, end_valid_date=data.end_valid_date)
        promotion.save()
        promotion = json.loads(promotion.to_json())
        return {'promotion': promotion}, 201


class PromotionDetailController(Resource):
    @jwt_required
    def get(self, promotion_id):
        promotion = Promotion.objects(pk=promotion_id).first()

        if not promotion:
            return {'message': 'Promotion not found.'}

        promotion = json.loads(promotion.to_json())
        return {'promotion': promotion}

    @jwt_required
    def put(self, promotion_id):
        user = get_jwt_identity()
        if user['user_type'] != 'merchant':
            return {'message': 'Only merchant can update promotion.'}, 400

        parser = reqparse.RequestParser()

        parser.add_argument('title', required=True, help='Title is required')
        parser.add_argument('description')
        parser.add_argument('image', type=FileStorage, location='files')
        parser.add_argument('start_valid_date')
        parser.add_argument('end_valid_date')

        promotion = Promotion.objects(pk=promotion_id)
        if not promotion:
            return {'message': 'Promotion not found.'}

        data = parser.parse_args()
        try:
            data['start_valid_date'] = datetime.strptime(
                data['start_valid_date'], '%Y-%m-%d %H:%M:%S')
        except:
            data['start_valid_date'] = None

        try:
            data['end_valid_date'] = datetime.strptime(
                data['end_valid_date'], '%Y-%m-%d %H:%M:%S')
        except:
            default_end_valid_date = datetime.utcnow()
            default_end_valid_date = default_end_valid_date.replace(year=3019)
            data['end_valid_date'] = default_end_valid_date

        if data.image:
            image = data['image']

            file_name = str(
                int(datetime.now(tz=timezone.utc).timestamp() * 1000))
            extension = image.filename.rsplit('.', 1)[1].lower()
            if '.' in image.filename and not extension in ALLOWED_EXTENSIONS:
                return {'message': 'File extension is not one of our supported types.'}, 400
            image_file = BytesIO()
            image.save(image_file)

            key_name = '{0}.{1}'.format(file_name, extension)
            content_type = FILE_CONTENT_TYPES[extension]
            bucket_name = 'reach-it'
            data['image'] = upload_s3(image_file, key_name,
                                      content_type, bucket_name)
        else:
            data['image'] = promotion['image']

        promotion.update_one(set__title=data.title, set__description=data.description, set__image=dataa['image'],
                             set__start_valid_date=data.start_valid_date, set__end_valid_date=data.end_valid_date)

        # Workaround to update last_modified_at
        promotion = Promotion.objects(
            pk=promotion_id).first()
        promotion.save()

        promotion = json.loads(promotion.to_json())
        return {'promotion': promotion}

    @jwt_required
    def delete(self, promotion_id):
        user = get_jwt_identity()
        if user['user_type'] != 'merchant':
            return {'message': 'Only merchant can delete promotion.'}, 400

        promotion = Promotion.objects(pk=promotion_id).first()
        if promotion:
            promotion.delete()

        return {'message': 'Promotion has been deleted.'}
