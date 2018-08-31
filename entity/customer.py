from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.sql import select, any_, join

from common.managers.dbManager import DBManager

from datetime import datetime
from .base import Base, BaseEntity
from .order import Order


# Entity Customer
class Customer(Base, BaseEntity):
    __tablename__ = 'Customers'

    # id
    id = Column(Integer, primary_key=True)
    # customer name
    name = Column(String(length=100))
    # tel
    phone = Column(String(20), unique=True, nullable=False)
    # email
    email = Column(String(50))
    # time created
    created_at = Column(Integer, default=int(datetime.now().timestamp()))
    # time updated
    updated_at = Column(Integer, default=int(datetime.now().timestamp()), onupdate=int(datetime.now().timestamp()))

    __table_args__ = (
        UniqueConstraint('email', 'phone'),
    )


# Entity CustomerOrder
class CustomerOrders(Base, BaseEntity):
    __tablename__ = 'CustomerOrders'

    # id
    id = Column(Integer, primary_key=True)
    # customer id
    customer_id = Column(Integer, ForeignKey('Customers.id'), nullable=False)
    # order id
    order_id = Column(Integer, ForeignKey('Orders.id'), nullable=False)

    __table_args__ = (
        # unique customer & order id
        UniqueConstraint('customer_id', 'order_id'),
    )

    @classmethod
    # select tags for units
    async def select_by_schedule(cls, schedule_ids: list, customer_ids: list = None, order_ids: list or set = None, fields: list=None) -> list:
        # join
        j = join(CustomerOrders, Order, CustomerOrders.order_id == Order.id, isouter=True)

        # set selected fields
        if not fields:
            fields = [CustomerOrders, Order]

        # query to db
        query = select(fields)

        # conditions
        # by tag_ids
        if order_ids:
            query = query.where(CustomerOrders.order_id == any_(order_ids))
        # by fleet_ids
        if schedule_ids:
            query = query.where(Order.schedule_id == any_(schedule_ids))
        # by unit_ids
        if customer_ids:
            query = query.where(CustomerOrders.customer_id == any_(customer_ids))

        # add join
        query = query.select_from(j)

        # return all records
        return await DBManager().query_fetch(query)