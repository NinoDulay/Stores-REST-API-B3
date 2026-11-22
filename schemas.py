# SCHEMAS = RULES PER ENDPOINT
from marshmallow import Schema, fields

# SCHEMA = VALIDATION/RULES
# ENSURE NA TAMA YUNG PAPASOK AND LALABAS NA DATA.

class PlainStoreSchema(Schema):
    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)

class PlainItemSchema(Schema):
    id = fields.Str(dump_only=True)
    name = fields.Str(required=True) 
    price = fields.Float(required=True)

class PlainTagSchema(Schema):
    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)

class ItemUpdateSchema(Schema):
    # DEFAULT: Optional
    name = fields.Str()
    price = fields.Float()


######
class StoreSchema(PlainStoreSchema):
    # PlainStoreSchema: id, name
    items = fields.List(fields.Nested(PlainItemSchema()), dump_only=True)
    tags = fields.List(fields.Nested(PlainTagSchema()), dump_only=True)

class ItemSchema(PlainItemSchema):
    # PlainItemSchema: id, name, price
    store_id = fields.Int(required=True)

    # One to Many
    store = fields.Nested(PlainStoreSchema(), dump_only=True)
    
    # Many to Many
    tags = fields.List(fields.Nested(PlainTagSchema(), dump_only=True))

class TagSchema(PlainTagSchema):
    # PlainTagSchema: id, name
    store_id = fields.Int()
    # One to Many
    store = fields.Nested(PlainStoreSchema(), dump_only=True)
    
    # Many to Many
    items = fields.Nested(PlainItemSchema(), dump_only=True)

# Schema = Rules for API Endpoints
class UserSchema(Schema):
    id = fields.Int(dump_only=True)   # Only need as output
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)  # Only need as input

## LOAD_ONLY = TRUE - required lang kapag mag POST Request (di lalabas sa GET)
## DUMP_ONLY = TRUE - Lalabas lang sa output (no need ilagay as input)










# SCHEMA = POST REQUESTS - PAPASOK SA API /GET REQUESTS - PALABAS



# CIRCULAR REFERENCING
# class StoreSchema(Schema):
#     id = fields.Str(dump_only=True)
#     name = fields.Str(required=True)
#     items = fields.List(fields.Nested(ItemSchema()), dump_only=True)

# class ItemSchema(Schema):
#     id = fields.Str(dump_only=True)
#     name = fields.Str(required=True) 
#     price = fields.Float(required=True)
#     store_id = fields.Int(required=True)
#     store = fields.Nested(StoreSchema(), dump_only=True)
