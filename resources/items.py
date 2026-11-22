from flask.views import MethodView
from flask_smorest import Blueprint, abort
from schemas import ItemSchema, ItemUpdateSchema

from sqlalchemy.exc import SQLAlchemyError

from db import db
from models import ItemModel
import uuid
from flask_jwt_extended import jwt_required

blp = Blueprint("items", __name__, description="Operation on items.")

@blp.route("/item")
class ItemList(MethodView):
    @blp.response(200, ItemSchema(many=True))
    def get(self):
        return ItemModel.query.all() # GET ALL ITEMS

    @jwt_required() # LOCK THIS ENDPOINT TO VALID USERS
    @blp.arguments(ItemSchema)  # POST
    @blp.response(200, ItemSchema)  # GET
    def post(self, request_body):
        # **kwargs
        new_item = ItemModel(**request_body)

        try:
            db.session.add(new_item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error has occured while creating an item")

        return new_item
            

@blp.route("/item/<string:item_id>")
class ItemList(MethodView):
    @blp.response(200, ItemSchema)
    def get(self, item_id):
        item = ItemModel.query.get_or_404(item_id)
        return item

    @jwt_required(fresh=True)
    def delete(self, item_id):
        item = ItemModel.query.get_or_404(item_id)

        # Delete an item
        db.session.delete(item)
        db.session.commit()

        return {"message": "Item Deleted."}

    @jwt_required()
    @blp.arguments(ItemUpdateSchema)
    @blp.response(200, ItemSchema)
    def put(self, request_body, item_id):
        item = ItemModel.query.get(item_id)

        # /item/1
        # If item exists
        if item:
            item.name = request_body["name"]
            item.price = request_body["price"]

        # Save the changes
        db.session.add(item)
        db.session.commit()

        return item

