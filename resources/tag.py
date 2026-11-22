from flask.views import MethodView
from flask_smorest import Blueprint, abort
from schemas import ItemSchema, ItemUpdateSchema, TagSchema

from sqlalchemy.exc import SQLAlchemyError

from db import db
from models import ItemModel, TagModel, StoreModel

import uuid
from flask_jwt_extended import jwt_required


blp = Blueprint("tags", __name__, description="Operation on tags.")

'''
TagsInStore:
GET  /store/{id}/tag    - Get all tags in a store
POST /store/{id}/tag   - Create a new tag

Tag:
GET /tag/{id} - Get information on a tag
DELETE /tag/{id} - Delete a tag, which should not have any items that are linked

LinkTagstoItems
POST /item/{tag}/tag/{id} - Link an item in a store with a tag from the same store
DELETE /item/{id}/tag/{id} - Unlink a tag from an item

'''
@blp.route("/store/<string:store_id>/tag")
class TagsInStore(MethodView):
    @blp.response(200, TagSchema(many=True))
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id) # 1
        return store.tags.all() # Return all tags that are related to the store.

    @jwt_required()
    @blp.arguments(TagSchema)
    @blp.response(201, TagSchema)
    def post(self, request_body, store_id):
        if TagModel.query.filter(
            TagModel.store_id == store_id,
            TagModel.name == request_body["name"]
        ).first():
            abort(400, message="A tag with that name already exists.")

        tag = TagModel(**request_body, store_id=store_id)
        try:
            db.session.add(tag)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error has occured while creating a tag.")

        return tag


@blp.route("/tag/<string:tag_id>")
class Tag(MethodView):
    @blp.response(200, TagSchema)
    def get(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)
        return tag

    @jwt_required()
    def delete(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)

        # Check if tag has items
        if tag.items:
            abort(400, message="Could not delete tag, make sure that tag is not linked to any item.")

        db.session.delete(tag)
        db.session.commit()

        return {"message": "Tag deleted."}, 202


'''
LinkTagstoItems
POST /item/{id}/tag/{id} - Link an item in a store with a tag from the same store
DELETE /item/{id}/tag/{id} - Unlink a tag from an item
'''

@blp.route("/item/<string:item_id>/tag/<string:tag_id>")
class LinkTagstoItems(MethodView):
    @jwt_required()
    @blp.response(200, TagSchema)
    def post(self, item_id, tag_id):
        # Get the item and tag you want to link
        # item = /item/1 - Guitar
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        # Before linking, make sure that the item and the tag is inside the same store
        if item.store_id != tag.store_id:
            abort(400, message="Make sure that the tag and the item is in the same store before linking.")

        # Add the tag in the item
        item.tags.append(tag)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occured while linking the tag.")

        return tag

    @jwt_required()
    def delete(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)


        item.tags.remove(tag)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occured while linking the tag.")

        return {"message": "Tag was deleted from the item!"}, 202