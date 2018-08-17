from sqlalchemy.sql import any_
from settings import logger
from entity.validators import ScheduleCreateSchema, ScheduleSchema
from .BaseModel import BaseModel
from entity.schedule import Schedule


# business-model by entity User
class ScheduleModel(BaseModel):
    def __init__(self, select_fields: set=set()):
        """
        :param select_fields: set, list fields for result
        """
        super().__init__(
            entity_cls=Schedule,
            all_fields=(
                'id',
                'name',
                'description',
                'email',
                'phone',
                'country_id',
                'city_id',
                'address',
                'flags',
                'data',
                'created_at',
                'updated_at',
            ),
            select_fields=select_fields
        )

    # Schema for create
    def _get_create_schema(self):
        return ScheduleCreateSchema()

    # Schema for update
    def _get_update_schema(self):
        return ScheduleSchema()

    # CREATE Entity
    async def create_entity(self, data: dict, **kwargs) -> tuple:
        result, errors = await super().create_entity(data, **kwargs)

        return result, errors

    # UPDATE Entity
    async def update_entity(self, data: dict, **kwargs) -> tuple:
        # update
        result, errors = await super().update_entity(data, **kwargs)

        return result, errors