from db import db
from models.item_tags import ItemTags


# Item Model
class ItemModel(db.Model):
    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True)

    # nullable = emptyable = (REQUIRED NA MAY LAMAN)
    name = db.Column(db.String(80), nullable=False)

    # xx.xx = Precision 2 (dalawang decimal point)
    price = db.Column(db.Float(precision=2), unique=False)

    # add a description
    description = db.Column(db.String, nullable=False, unique=False)

    # Pwede maulit (unique=False)
    # PAANO ICOCONNECT SA TABLE NA STORES?????
    store_id = db.Column(db.Integer, db.ForeignKey("stores.id"), nullable=False, unique=False)

    # Relationship (One to Many)
    store = db.relationship("StoreModel", back_populates="items")


    # Relationship (Many to Many)
    tags = db.relationship("TagModel", back_populates="items", secondary=ItemTags.__table__) 
