from sqlalchemy.sql import any_
from marshmallow import Schema

from .BaseModel import BaseModel

from entity.validators import OrderCreateSchema, OrderSchema
from entity.schedule import Schedule
from entity.order import Order


# business-model by entity User
class OrderModel(BaseModel):
    def __init__(self, allowed_schedule_ids: set, select_fields: set=set(), creater_id: int = -1):
        """
        :param select_fields: set, list fields for result
        """
        super().__init__(
            entity_cls=Order,
            all_fields=(
                'id',
                'time',
                'description',
                'status',
                'payment',
                'auto_confirm',
                'customer_id',
                'schedule_id',
                'created_at',
                'updated_at',
            ),
            select_fields=select_fields
        )
        # get creter id for current session
        self.creater_id = creater_id
        # allowed schedules
        self.allowed_schedule_ids = allowed_schedule_ids

    # Schema for create
    @classmethod
    def _get_create_schema(self) -> Schema:
        return OrderCreateSchema()

    # Schema for update
    @classmethod
    def _get_update_schema(self) -> Schema:
        return OrderSchema()

    # GET Entity
    async def get_entities(self, ids: list, schedule_ids: set = None, customer_ids: set = None, filter_name: str = None, status: str = None) -> tuple:
        # result vars
        result = []
        errors = []

        # conditions by select users
        conditions = await self._get_base_condition()

        allowed_schedule_ids = self.allowed_schedule_ids
        if schedule_ids:
            # condition by allowed Schedules
            allowed_schedule_ids = self.allowed_schedule_ids.intersection(schedule_ids)

        # conditions for select details, by allowed schedule
        conditions = [self.entity_cls.schedule_id == any_(allowed_schedule_ids)]

        # condition by selector ids
        if ids:
            conditions.append(self.entity_cls.id == any_(ids))

        # condition by selector name
        if customer_ids:
            conditions.append(self.entity_cls.customer_id == any_(customer_ids))

        # condition by selector name
        if filter_name:
            conditions.append(self.entity_cls.name.contains(filter_name))

        # condition by order status
        if status:
            conditions.append(self.entity_cls.status.contains(status))

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
            self.calc_result(records, ids, result, errors)

        return result, errors

    # CREATE Entity
    async def create_entity(self, data: dict, **kwargs) -> tuple:
        # result vars
        result = []
        errors = []

        # schedule id from request params
        sch_ids = data['schedule_id']
        customer_id = data['customer_id']

        # if schedule accessable
        if sch_ids and customer_id:
            result, errors = await super().create_entity(data, **kwargs)
        else:
            errors = self.get_error_item('id', 'You have not such schedule')

        # get entites
        return result, errors

    # UPDATE Entity
    async def update_entity(self, data: dict, **kwargs) -> tuple:
        # result vars
        result = []
        errors = []

        # schedule id from request params
        sch_ids = data['schedule_id']

        # allowed schedules
        allow_schedule_items = await Schedule.select_where(
            cls_fields=[Schedule.id],
            conditions=[Schedule.creater_id == self.creater_id, Schedule.id == sch_ids]
        )
        # if schedule accessable
        if allow_schedule_items:
            result, errors = await super().update_entity(data, **kwargs)
        else:
            errors = self.get_error_item('id', 'You have not such schedule')

        # get entites
        return result, errors