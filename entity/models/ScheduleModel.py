from sqlalchemy.sql import any_
from settings import logger

from .BaseModel import BaseModel

from entity.validators import ScheduleCreateSchema, ScheduleSchema
from entity.schedule import Schedule

from common.managers.sessionManager import SessionManager


# business-model by entity User
class ScheduleModel(BaseModel):
    def __init__(self, select_fields: set=set(), creater_id: int = -1):
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
        # get creter id for current session
        self.creater_id = creater_id

    # Schema for create
    def _get_create_schema(self):
        return ScheduleCreateSchema()

    # Schema for update
    def _get_update_schema(self):
        return ScheduleSchema()

    # GET Entity
    async def get_entities(self, ids: list, filter_name: str = None) -> tuple:
        # result vars
        result = []
        errors = []

        # conditions by select users
        conditions = []

        # condition by allowed Fleets
        conditions.append(self.entity_cls.creater_id == self.creater_id)

        # condition by selector ids
        if ids:
            conditions.append(self.entity_cls.id == any_(ids))

        # condition by selector name
        if filter_name:
            conditions.append(self.entity_cls.name.contains(filter_name))

        # select by conditions
        records = await self.entity_cls.select_where(
            str_fields=self.select_fields,
            conditions=conditions
        )

        # ids by selected items
        select_ids = set()
        # generate result list
        for record in records:
            select_ids.add(record['id'])
            result.append(self.get_result_item(record, self.select_fields))

        # add not selected items in errors
        if ids:
            # get ids not selected
            ids = set(ids)
            # find diff
            ids_diff = ids.difference(select_ids)
            # add errors by not found ids
            for id_diff in ids_diff:
                errors.append(
                    self.get_error_item(selector='id', reason='Schedule is not found in the Fleets', value=id_diff))

        return result, errors

    # CREATE Entity
    async def create_entity(self, data: dict, **kwargs) -> tuple:
        # add creter id in request data
        data['creater_id'] = self.creater_id

        # run method in BaseModel
        return await super().create_entity(data)

    # UPDATE Entity
    async def update_entity(self, data: dict, **kwargs) -> tuple:
        # update
        # add creter id in request data
        data['creater_id'] = self.creater_id

        # run method in BaseModel
        return await super().update_entity(data)