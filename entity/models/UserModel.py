from entity.validators import UserCreateSchema, UserSchema
from marshmallow import Schema, fields, validate
from .BaseModel import BaseModel
from entity.user import User


# business-model by entity User
class UserModel(BaseModel):
    def __init__(self, select_fields: set=set()):
        """
        :param select_fields: set, list fields for result
        """
        super().__init__(
            entity_cls=User,
            all_fields=(
                'id',
                'name',
                'organization',
                'description',
                'login',
                'password',
                'email',
                'phone',
                'country_id',
                'city_id',
                'address',
                'mail_agreement',
                'flags',
                'data'
            ),
            select_fields=select_fields
        )

    @classmethod
    def _get_create_schema(cls) -> Schema:
        # schema for create entity
        class UserCreateSchema(Schema):
            login = fields.String(required=True, validate=validate.Length(min=4, max=20))
            password = fields.String(load_only=True, validate=validate.Length(min=4, max=20))
            email = fields.Email(required=True)
            phone = fields.String(required=True)

        return UserCreateSchema()

    @classmethod
    def _get_update_schema(cls) -> Schema:
        # schema for update entity
        class UserUpdateSchema(Schema):
            id = fields.Integer(required=True)
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

        return UserUpdateSchema()

    # CREATE Entity
    async def create_entity(self, data: dict, **kwargs) -> tuple:
        # crypt code
        if data.get(User.password.name):
            data[User.password.name] = User.p_encrypt(data[User.password.name])

        result, errors = await super().create_entity(data, **kwargs)

        return result, errors

    # UPDATE Entity
    async def update_entity(self, data: dict, **kwargs) -> tuple:
        # crypt code
        if data.get(User.password.name):
            data[User.password.name] = User.p_encrypt(data[User.password.name])
        # update
        result, errors = await super().update_entity(data, **kwargs)

        return result, errors