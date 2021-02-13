from flask_jwt_extended import jwt_required
from flask_restful import Resource

from models.store import StoreModel


STORE_ALREADY_EXIST = "The store with name '{}' already exists"
ERROR_INSERTING = "DB error occurred while db insertion"
STORE_NOT_FOUND = "The store is not found"
STORE_DELETED = "The store is deleted"


class Store(Resource):
    def get(self, name: str):
        store = StoreModel.find_by_name(name)
        if store:
            return store.json, 200
        return {"message": STORE_NOT_FOUND}, 404

    @jwt_required
    def post(self, name: str):
        if StoreModel.find_by_name(name):
            return {"message": STORE_ALREADY_EXIST.format(name)}, 409

        store = StoreModel(name)
        try:
            store.save_to_db()
        except:
            return {"message": ERROR_INSERTING}, 500

        return store.json, 201

    @jwt_required
    def delete(self, name: str):
        store = StoreModel.find_by_name(name)
        if store:
            store.delete_from_db()
            return {"message": STORE_DELETED}
        return {"message": STORE_NOT_FOUND}, 404


class StoreList(Resource):
    @jwt_required
    def get(self):
        return {"stores": [store.json for store in StoreModel.find_all()]}
