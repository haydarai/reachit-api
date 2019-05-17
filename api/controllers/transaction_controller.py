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
        data = request.get_json()

        user = get_jwt_identity()
        transaction = Transaction(user=user['id'], items=data['items'])
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
        data = request.get_json()

        transaction = Transaction.objects(
            pk=transaction_id)

        if not transaction:
            return {'message': 'Transaction not found.'}

        transaction.update_one(set__items=data['items'])

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
