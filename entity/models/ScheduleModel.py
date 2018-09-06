from sqlalchemy.sql import any_
from settings import logger

from .BaseModel import BaseModel

from entity.validators import ScheduleCreateSchema, ScheduleSchema
from entity.schedule import Schedule

from common.managers.sessionManager import SessionManager


# schedule for Users
class ScheduleModel(BaseModel):
    def __init__(self, allowed_schedule_ids: set, select_fields: set=set(), creater_id: int = -1):
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
                'activate',
            ),
            select_fields=select_fields,
            conditions=[Schedule.activate == True]
        )
        # get creter id for current session
        self.creater_id = creater_id

    # Schema for create
    @classmethod
    def _get_create_schema(self):
        return ScheduleCreateSchema()

    # Schema for update
    @classmethod
    def _get_update_schema(self):
        return ScheduleSchema()

    # GET Entity
    async def get_entities(self, ids: list, filter_name: str = None) -> tuple:
        # result vars
        result = []
        errors = []

        # conditions by allowed creaters
        conditions = await self.get_base_condition()

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

        self.calc_result(records, ids, result, errors)

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


# schedule for Customers
class ScheduleOnlineModel(BaseModel):
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
            select_fields=select_fields,
            # add base-conditions
            conditions=[self.entity_cls.creater_id == creater_id]
        )
        # get creter id for current session
        self.creater_id = creater_id

    # Schema for create
    @classmethod
    def _get_create_schema(self):
        return ScheduleCreateSchema()

    # Schema for update
    @classmethod
    def _get_update_schema(self):
        return ScheduleSchema()

    # GET Entity
    async def get_entities(self, ids: list, filter_name: str = None) -> tuple:
        # result vars
        result = []
        errors = []

        # conditions by allowed creaters
        conditions = self.get_base_condition()

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

        self.calc_result(records, ids, result, errors)

        return result, errors