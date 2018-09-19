from sqlalchemy.sql import any_
from marshmallow import Schema, fields
from datetime import datetime

from .BaseModel import BaseModel

from entity.schedule import Schedule
from entity.schDetail import SCHDetail
from entity.order import Order


# business-model by entity User
class ScheduleDetailModel(BaseModel):
    def __init__(self, allowed_schedule_ids: set, select_fields: set=set(), creater_id: int = -1):
        """
        :param select_fields: set, list fields for result
        """
        super().__init__(
            entity_cls=SCHDetail,
            all_fields=(
                'id',
                'time',
                'description',
                'members',
                'price',
                'schedule_id',
            ),
            select_fields=select_fields,
            conditions=[SCHDetail.schedule_id == any_(allowed_schedule_ids)]
        )
        # get creter id for current session
        self.creater_id = creater_id
        # allowed schedules
        self.allowed_schedule_ids = allowed_schedule_ids

    # Schema for create
    @classmethod
    def _get_create_schema(self) -> Schema:
        class ScheduleDetailCreateSchema(Schema):
            time = fields.Integer(required=True, default=datetime.now())
            description = fields.String(length=200)
            members = fields.Integer(default=1)
            schedule_id = fields.Integer(required=True)
            price = fields.Float(default=1)
        return ScheduleDetailCreateSchema()

    # Schema for update
    @classmethod
    def _get_update_schema(self) -> Schema:
        class ScheduleDetailUpdateSchema(Schema):
            id = fields.Integer(required=True)
            time = fields.Integer(required=True, default=datetime.now())
            description = fields.String(length=200)
            members = fields.Integer(default=1)
            schedule_id = fields.Integer(required=True)
            price = fields.Float(default=1)
        return ScheduleDetailUpdateSchema()

    # GET Entity
    async def get_entities(self, ids: list, schedule_ids: set = None) -> tuple:
        # result vars
        result = []
        errors = []

        # conditions for select details, by allowed schedule
        conditions = await self._get_base_condition()

        # condition by selector ids
        if ids:
            conditions.append(self.entity_cls.id == any_(ids))

        # condition by schedule_ids
        # get intersection schedules
        if schedule_ids:
            conditions.append(self.entity_cls.schedule_id == any_(schedule_ids))

        # select by conditions
        records = await self.entity_cls.select_where(
            str_fields=self.select_fields,
            conditions=conditions
        )

        #  ---- result data format ----
        # schedule_id: list()
        #  ----------------------------

        format_result = dict()
        # format details
        for detail_item in records:
            format_result_data = format_result.setdefault(detail_item['schedule_id'], list())
            format_result_data.append(self.get_result_item(detail_item, self.select_fields))

        if format_result:
            result.append(format_result)

        return result, errors

    # CREATE Entity
    async def create_entity(self, data: dict, **kwargs) -> tuple:
        # result vars
        result = []

        # schedule id from request params
        sch_id = data.get('schedule_id', -1)

        # if schedule accessable
        if sch_id in self.allowed_schedule_ids:
            result, errors = await super().create_entity(data, **kwargs)
        else:
            errors = self.get_error_item('id', 'Access denied...')

        # get entites
        return result, errors

