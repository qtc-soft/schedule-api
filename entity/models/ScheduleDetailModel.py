from sqlalchemy.sql import any_

from .BaseModel import BaseModel

from entity.validators import ScheduleDetailCreateSchema, ScheduleDetailSchema
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
                'schedule_id',
            ),
            select_fields=select_fields
        )
        # get creter id for current session
        self.creater_id = creater_id
        # allowed schedules
        self.allowed_schedule_ids = allowed_schedule_ids

    # Schema for create
    @classmethod
    def _get_create_schema(self):
        return ScheduleDetailCreateSchema()

    # Schema for update
    @classmethod
    def _get_update_schema(self):
        return ScheduleDetailSchema()

    # GET Entity
    async def get_entities(self, ids: list, schedule_ids: set = None) -> tuple:
        # result vars
        result = []
        errors = []

        allowed_schedule_ids = self.allowed_schedule_ids
        if schedule_ids:
            # condition by allowed Schedules
            allowed_schedule_ids = self.allowed_schedule_ids.intersection(schedule_ids)

        # conditions for select details, by allowed schedule
        conditions = [self.entity_cls.schedule_id == any_(allowed_schedule_ids)] if ids else []

        # condition by selector ids
        if ids:
            conditions.append(self.entity_cls.id == any_(ids))

        # select by conditions
        detail_items = await self.entity_cls.select_where(
            str_fields=self.select_fields,
            conditions=conditions
        )

        # self.calc_result(detail_items, ids, result, errors)

        order_items = await Order.select_where(
            cls_fields=[Order.id, Order.time],
            conditions=[Order.schedule_id == any_(allowed_schedule_ids)]
        )

        format_result = dict()
        #  ---- result data format ----
        # schedule_id: {
        #   time: {
        #       orders: [],
        #       details: []
        #   }
        # }
        #  ----------------------------
        # format details
        for detail_item in detail_items:
            format_result_data = format_result.setdefault(detail_item['schedule_id'], dict(orders=list(), details=list()))
            format_result_data['details'].append(self.get_result_item(detail_item, self.select_fields))

        # format orders
        for order_item in order_items:
            if format_result[order_item['schedule_id']] and format_result[order_item['schedule_id']]['orders']:
                format_result[order_item['schedule_id']]['orders'].add(order_item)

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

    # UPDATE Entity
    async def update_entity(self, data: dict, **kwargs) -> tuple:
        # result vars
        result = []
        errors = []

        # schedule id from request params
        sch_id = data.get('schedule_id', -1)

        # if schedule accessable
        if sch_id in self.allowed_schedule_ids:
            result, errors = await super().update_entity(data, **kwargs)
        else:
            errors = self.get_error_item('id', 'You have not such schedule')

        # get entites
        return result, errors