from sqlalchemy.sql import any_

from .BaseModel import BaseModel

from entity.validators import CustomerCreateSchema, CustomerSchema
from entity.customer import Customer
from entity.order import Order
from entity.schedule import Schedule


# business-model by entity User
class CustomerModel(BaseModel):
    def __init__(self, allowed_schedule_ids: set, select_fields: set=set()):
        """
        :param select_fields: set, list fields for result
        """
        super().__init__(
            entity_cls=Customer,
            all_fields=(
                'id',
                'name',
                'phone',
                'email',
                'created_at',
                'updated_at',
            ),
            select_fields=select_fields
        )
        # allowed schedules
        self.allowed_schedule_ids = allowed_schedule_ids

    # Schema for create
    def _get_create_schema(self):
        return CustomerCreateSchema()

    # Schema for update
    def _get_update_schema(self):
        return CustomerSchema()

    # GET Entity
    async def get_entities(self, ids: list, schedule_ids: set = None, filter_name: str = None) -> tuple:
        result = []
        errors = []

        # default filter customers only by ids in request
        allowed_customer_ids = ids

        # default all schedules accessable
        allowed_schedule_ids = self.allowed_schedule_ids

        # if need specific schedule data
        if schedule_ids:
            # condition by allowed Schedules
            allowed_schedule_ids = self.allowed_schedule_ids.intersection(schedule_ids)

            # get orders for some schedules
            order_items = await Order.select_where(
                cls_fields=[Order.id, Order.schedule_id],
                conditions=[Order.schedule_id == any_(allowed_schedule_ids)]
            )
            # get customer ids form orders
            allowed_customer_ids = [order_item['customer_id'] for order_item in order_items]
            if ids:
                allowed_customer_ids = allowed_customer_ids.intersection(ids)


        # base conditions
        conditions = self.get_base_condition()

        # condition by selector ids
        if allowed_customer_ids:
            conditions.append(self.entity_cls.id == any_(allowed_customer_ids))

        # condition by selector name
        if filter_name:
            conditions.append(self.entity_cls.name.contains(filter_name))

        # select by conditions
        customer_items = await self.entity_cls.select_where(
            str_fields=self.select_fields,
            conditions=conditions
        )

        # format data
        format_result = dict()
        # generate result list
        for customer_item in customer_items:
            format_result.setdefault(customer_item['schedule_id'], [])
            format_result[customer_item['schedule_id']].append(self.get_result_item(customer_item, self.select_fields))

        # add not selected items in errors
        if ids:
            # get ids not selected
            ids = set(ids)
            ids_diff = ids.difference(select_ids)
            # add errors by not found ids
            for id_diff in ids_diff:
                errors.append(
                    self.get_error_item(selector='id', reason='Customer or schedule-detail is not found', value=id_diff))
        result.append(format_result)
        return result, errors

    # CREATE Entity
    async def create_entity(self, data: dict, **kwargs) -> tuple:
        # result vars
        result = []
        errors = []

        # schedule id from request params
        sch_ids = data['schedule_id']

        # allowed schedules
        allow_schedule_items = await Customer.select_where(
            cls_fields=[Customer.id],
            conditions=[Customer.creater_id == self.creater_id, Customer.id == sch_ids]
        )
        # if schedule accessable
        if allow_schedule_items:
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
        allow_schedule_items = await Customer.select_where(
            cls_fields=[Customer.id],
            conditions=[Customer.creater_id == self.creater_id, Customer.id == sch_ids]
        )
        # if schedule accessable
        if allow_schedule_items:
            result, errors = await super().update_entity(data, **kwargs)
        else:
            errors = self.get_error_item('id', 'You have not such schedule')

        # get entites
        return result, errors