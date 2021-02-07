from flask_jwt_extended import jwt_required, get_jwt_claims, jwt_optional, get_jwt_identity, fresh_jwt_required
from flask_restful import Resource, reqparse

from models.item import ItemModel


class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        'price',
        type=float,
        required=True,
        help="The 'price' field is required!"
    )
    parser.add_argument(
        'store_id',
        type=int,
        required=True,
        help="The 'store_id' field is required!"
    )

    @jwt_required
    def get(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            return item.json, 200
        return {'message': 'The item is not found'}, 404

    @fresh_jwt_required
    def post(self, name):
        if ItemModel.find_by_name(name):
            return {'message': f'The item with name "{name}" already exists'}, 409

        data = Item.parser.parse_args()

        item = ItemModel(name, **data)

        try:
            item.save_to_db()
        except:
            return {"message": "DB error occurred while db insertion"}, 500

        return item.json, 201

    @jwt_required
    def delete(self, name):
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'message': 'You don\'t have permissions'}, 403
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
            return {'message': 'The item is deleted'}
        return {'message': 'The item is not found'}, 404

    @jwt_required
    def put(self, name):
        data = Item.parser.parse_args()

        item = ItemModel.find_by_name(name)

        if item is None:
            item = ItemModel(name, **data)
        else:
            item.price = data['price']
            item.store_id = data['store_id']
        item.save_to_db()

        return item.json


class ItemList(Resource):
    @jwt_optional
    def get(self):
        user_id = get_jwt_identity()
        items = [item.json for item in ItemModel.find_all()]
        if user_id:
            return {'items': items}, 200
        return {
                   'items': [item['name'] for item in items],
                   'message': 'More data available if you log in.'
               }, 200
