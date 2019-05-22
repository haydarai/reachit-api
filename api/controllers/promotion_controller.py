from api.models.promotion_model import Promotion
from flask_restful import Resource, reqparse
from flask_jwt_extended import (
    jwt_required, get_jwt_identity
)
from datetime import datetime
import json


class PromotionController(Resource):
    @jwt_required
    def get(self):
        user = get_jwt_identity()
        current_time = datetime.utcnow()
        promotions = Promotion.objects(
            start_valid_date__lte=current_time, end_valid_date__gte=current_time)
        promotions = json.loads(promotions.to_json())
        return {'promotions': promotions}

    @jwt_required
    def post(self):
        user = get_jwt_identity()
        if user['user_type'] != 'merchant':
            return {'message': 'Only merchant can create promotion.' }, 400

        parser = reqparse.RequestParser()

        parser.add_argument('title', required=True, help='Title is required')
        parser.add_argument('description')
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
            default_end_valid_date.year = '3019'
            data['end_valid_date'] = default_end_valid_date

        promotion = Promotion(creator=user['id'], title=data.title, description=data.description,
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
            return {'message': 'Only merchant can update promotion.' }, 400

        parser = reqparse.RequestParser()

        parser.add_argument('title', required=True, help='Title is required')
        parser.add_argument('description', required=True, help='Description is required')
        parser.add_argument('start_valid_date', required=True, help='Start valid date is required')
        parser.add_argument('end_valid_date', required=True, help='End valid date is required')

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
            default_end_valid_date.year = '3019'
            data['end_valid_date'] = default_end_valid_date

        promotion = Promotion.objects(pk=promotion_id)
        if not promotion:
            return {'message': 'Promotion not found.'}

        promotion.update_one(set__title=data.title, set__description=data.description,
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
            return {'message': 'Only merchant can delete promotion.' }, 400

        promotion = Promotion.objects(pk=promotion_id).first()
        if promotion:
            promotion.delete()

        return {'message': 'Promotion has been deleted.'}
