from sqlalchemy.sql import any_
from settings import logger
from entity.validators import UserCreateSchema, UserSchema
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
                'description',
                'password',
                'email',
                'flags',
                'data',
                'created_at',
                'updated_at',
            ),
            select_fields=select_fields
        )

    # Schema for create
    def _get_create_schema(self):
        return UserCreateSchema()

    # Schema for update
    def _get_update_schema(self):
        return UserSchema()

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