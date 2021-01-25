from flask_jwt import jwt_required
from flask_restful import Resource, reqparse

from models.store import StoreModel


class Store(Resource):

    def get(self, name):
        store = StoreModel.find_by_name(name)
        if store:
            return store.json, 200
        return {'message': 'The store is not found'}, 404

    def post(self, name):
        if StoreModel.find_by_name(name):
            return {'message': f'The store with name "{name}" already exists'}, 409

        store = StoreModel(name)
        try:
            store.save_to_db()
        except:
            return {'message': 'DB error occurred while db insertion'}, 500

        return store.json, 201

    def delete(self, name):
        store = StoreModel.find_by_name(name)
        if store:
            store.delete_from_db()
            return {'message': 'The store is deleted'}
        return {'message': 'The store is not found'}, 404


class StoreList(Resource):
    def get(self):
        return {'stores': [store.json for store in StoreModel.query.all()]}
