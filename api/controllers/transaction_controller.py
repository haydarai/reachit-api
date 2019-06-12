from api.models.transaction_model import Transaction
from flask import request
from flask_restful import Resource, reqparse
from flask_jwt_extended import (
    jwt_required, get_jwt_identity
)
import json


class TransactionController(Resource):
    @jwt_required
    def get(self):
        user = get_jwt_identity()
        transactions = Transaction.objects(user=user['id']).exclude('user')
        transactions = json.loads(transactions.to_json())
        return {'transactions': transactions}

    @jwt_required
    def post(self):
        user = get_jwt_identity()
        data = request.get_json()

        if data['items'] is None:
            return {'message': 'Items is required.'}, 400

        if data['location'] is None:
            data['location'] = ''

        if data['merchant'] is None:
            data['merchant'] = ''

        if data['city'] is None:
            data['city'] = ''

        if data['country'] is None:
            data['country'] = ''

        transaction = Transaction(
            user=user['id'], items=data['items'], location=data['location'],
            merchant=data['merchant'], city=data['city'], country=data['country'])
        transaction.save()
        transaction = json.loads(transaction.to_json())
        return {'transaction': transaction}, 201


class TransactionDetailController(Resource):
    @jwt_required
    def get(self, transaction_id):
        transaction = Transaction.objects(pk=transaction_id).first()

        if not transaction:
            return {'message': 'Transaction not found.'}

        transaction = json.loads(transaction.to_json())
        return {'transaction': transaction}

    @jwt_required
    def put(self, transaction_id):
        transaction = Transaction.objects(
            pk=transaction_id)

        if not transaction:
            return {'message': 'Transaction not found.'}

        parser = reqparse.RequestParser()

        parser.add_argument('items', required=True,
                            help='Items list is required')
        parser.add_argument('location', required=True,
                            help='Location is required')
        parser.add_argument('merchant', required=True,
                            help='Merchant is required')
        parser.add_argument('city', required=True,
                            help='City is required')
        parser.add_argument('country', required=True,
                            help='Country is required')

        data = parser.parse_args()

        transaction.update_one(
            set__items=data['items'], set__location=data['location'],
            set__merchant=data['merchant'], set__city=data['city'],
            set__country=data['country'])

        # Workaround to update last_modified_at
        transaction = Transaction.objects(
            pk=transaction_id).first()
        transaction.save()

        transaction = json.loads(transaction.to_json())
        return {'transaction': transaction}

    @jwt_required
    def delete(self, transaction_id):
        transaction = Transaction.objects(pk=transaction_id).first()
        if transaction:
            transaction.delete()

        return {'message': 'Transaction has been deleted.'}
