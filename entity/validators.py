from marshmallow import Schema, fields, UnmarshalResult


# -- Base Schemas --
# schema for create new base entity
class EntityCreateSchema(Schema):
    description = fields.String(length=200)
    flags = fields.Integer()
    created_at = fields.Integer(dump_only=True)
    updated_at = fields.Integer(dump_only=True)


# schema for update base entity
class EntitySchema(EntityCreateSchema):
    id = fields.Integer()
# -- END Base Schemas --


class CountryCreateSchema(EntityCreateSchema):
    label = fields.String(length=100)


class CountrySchema(CountryCreateSchema):
    id = fields.Integer()


# -- Schedule Detail Schemas --
# schema for create new schedule detail entity
class OrderCreateSchema(EntityCreateSchema):
    time = fields.Integer()
    description = fields.String(length=200)
    status = fields.String(50)
    payment = fields.Boolean()
    auto_confirm = fields.Boolean()
    customer_id = fields.Integer()
    schedule_id = fields.Integer()


class OrderSchema(OrderCreateSchema):
    id = fields.Integer()
# -- END Schedule Detail schemas --
