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


# -- User Schemas --
# schema for create new user entity
class UserCreateSchema(EntityCreateSchema):
    name = fields.String(length=100)
    organization = fields.String(length=200)
    description = fields.String(length=200)
    login = fields.String(length=100)
    password = fields.String(load_only=True)
    email = fields.Email()
    phone = fields.String(length=50)
    country_id = fields.Integer()
    city_id = fields.Integer()
    address = fields.String(length=200)
    mail_agreement = fields.Boolean()
    data = fields.Dict()
    flags = fields.Integer()


class UserSchema(UserCreateSchema):
    id = fields.Integer()
# -- END User schemas --


class CountryCreateSchema(EntityCreateSchema):
    label = fields.String(length=100)


class CountrySchema(CountryCreateSchema):
    id = fields.Integer()

# -- Schedule Schemas --
# schema for create new schedule entity
class ScheduleCreateSchema(EntityCreateSchema):
    name = fields.String(length=100)
    description = fields.String(length=200)
    email = fields.Email()
    phone = fields.String(length=50)
    creater_id = fields.Integer()
    country_id = fields.Integer()
    city_id = fields.Integer()
    address = fields.String(length=200)
    data = fields.Dict()
    flags = fields.Integer()


class ScheduleSchema(ScheduleCreateSchema):
    id = fields.Integer()
# -- END Schedule schemas --


# -- Schedule Detail Schemas --
# schema for create new schedule detail entity
class ScheduleDetailCreateSchema(EntityCreateSchema):
    time = fields.Integer()
    description = fields.String(length=200)
    members = fields.Integer()
    schedule_id = fields.Integer()


class ScheduleDetailSchema(ScheduleDetailCreateSchema):
    id = fields.Integer()
# -- END Schedule Detail schemas --


# -- Customer Schemas --
# schema for create new schedule entity
class CustomerCreateSchema(EntityCreateSchema):
    name = fields.String(length=100)
    email = fields.Email()
    phone = fields.String(length=50)


class CustomerSchema(ScheduleCreateSchema):
    id = fields.Integer()
# -- END Customer schemas --