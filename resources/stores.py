from flask.views import MethodView
from flask_smorest import Blueprint, abort
from schemas import StoreSchema

from models import StoreModel

from sqlalchemy.exc import SQLAlchemyError

from db import db
import uuid
from flask_jwt_extended import jwt_required, get_jwt

# Create the blueprint
blp = Blueprint("stores", __name__, description="Operation on stores.")


# Singular Store
@blp.route("/store/<string:store_id>")
class Store(MethodView):
    @blp.response(200, StoreSchema)
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        return store

    @jwt_required(fresh=True)
    def delete(self, store_id):
        store = StoreModel.query.get_or_404(store_id)

        db.session.delete(store)
        db.session.commit()

        return {"message": "Store deleted."}


@blp.route("/store")
class StoreList(MethodView):
    # many=True = LIST OF STORESCHEMA
    @blp.response(200, StoreSchema(many=True))
    def get(self):
        return StoreModel.query.all()

    @jwt_required()
    @blp.arguments(StoreSchema) # INPUT - POST
    @blp.response(200, StoreSchema) # OUTPUT - GET
    def post(self, request_data):
        store = StoreModel(**request_data)

        try:
            db.session.add(store)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error has occured while creating a store.")

        return store
        




