from flask_jwt_extended import jwt_required, fresh_jwt_required
from flask_restful import Resource, reqparse

from models.item import ItemModel


REQUIRED_ERROR = "This field '{}' is required!"
NAME_ALREADY_EXIST = "The item with name '{}' already exists"
ERROR_INSERTING = "DB error occurred while db insertion"
ITEM_NOT_FOUND = "The item is not found"
ITEM_DELETED = "The item is deleted"


class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        "price", type=float, required=True, help=REQUIRED_ERROR.format("price")
    )
    parser.add_argument(
        "store_id", type=int, required=True, help=REQUIRED_ERROR.format("store_id")
    )

    def get(self, name: str):
        item = ItemModel.find_by_name(name)
        if item:
            return item.json, 200
        return {"message": ITEM_NOT_FOUND}, 404

    @fresh_jwt_required
    def post(self, name: str):
        if ItemModel.find_by_name(name):
            return {"message": NAME_ALREADY_EXIST.format(name)}, 409

        data = Item.parser.parse_args()

        item = ItemModel(name, **data)

        try:
            item.save_to_db()
        except:
            return {"message": ERROR_INSERTING}, 500

        return item.json, 201

    @jwt_required
    def delete(self, name: str):
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
            return {"message": ITEM_DELETED}
        return {"message": ITEM_NOT_FOUND}, 404

    @jwt_required
    def put(self, name: str):
        data = Item.parser.parse_args()

        item = ItemModel.find_by_name(name)

        if item is None:
            item = ItemModel(name, **data)
        else:
            item.price = data["price"]
            item.store_id = data["store_id"]
        item.save_to_db()

        return item.json


class ItemList(Resource):
    def get(self):
        return {"items": [item.json for item in ItemModel.find_all()]}, 200
