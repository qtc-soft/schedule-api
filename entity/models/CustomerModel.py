from sqlalchemy.sql import any_
from marshmallow import Schema

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
    @classmethod
    def _get_create_schema(self) -> Schema:
        return CustomerCreateSchema()

    # Schema for update
    @classmethod
    def _get_update_schema(self) -> Schema:
        return CustomerSchema()

    # GET Entity
    async def get_entities(self, ids: list, schedule_ids: set = None, filter_name: str = None) -> tuple:
        result = []
        errors = []

        # default filter customers only by ids in request
        allowed_customer_ids = ids

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
        conditions = await self._get_base_condition()

        # condition by selector ids
        if allowed_customer_ids:
            conditions.append(self.entity_cls.id == any_(allowed_customer_ids))

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
