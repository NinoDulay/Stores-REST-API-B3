from db import db
from models.item_tags import ItemTags

class TagModel(db.Model):
    __tablename__ = "tags"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(80), unique=False, nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey("stores.id"))

    # One to Many: db.relationship
    store = db.relationship("StoreModel", back_populates="tags")

    # Many to Many
    # secondary = Conjunction
    items = db.relationship("ItemModel", back_populates="tags", secondary=ItemTags.__table__)


# GET /tag/1
# {
#     "name" :"guitar",
#     "store": {},
#     "items": {}
# }