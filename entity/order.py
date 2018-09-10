from datetime import datetime

from sqlalchemy import Column, Integer, String, types, Boolean, ForeignKey, DateTime, DATETIME, UniqueConstraint, Enum
from sqlalchemy.sql import select, any_, join

from .base import Base, BaseEntity

from common.managers.dbManager import DBManager

import enum
class OrderStatusEnum(enum.Enum):
    # order booking
    booking = 1
    # order confirmed
    confirmed = 2
    # order rejected
    rejected = 3
    # order paid
    paid = 4


# Entity Order
class Order(Base, BaseEntity):
    __tablename__ = 'Orders'

    # id
    id = Column(Integer, primary_key=True)
    # order time must be equal time from schedule details
    time = Column(Integer, nullable=False)
    # schedule
    schedule_id = Column(Integer, ForeignKey('Schedules.id', ondelete='CASCADE'), nullable=False)
    #
    customer_id = Column(Integer, ForeignKey('Customers.id'), nullable=False)
    # description from customer
    description = Column(String(length=200))
    # status
    status = Column(Enum(OrderStatusEnum), default=OrderStatusEnum.booking, nullable=False)
    # online paiment
    paiment = Column(Boolean, default=False)
    # auto confirm by phone
    auto_confirm = Column(Boolean, default=True)
    # time created
    created_at = Column(Integer, default=int(datetime.now().timestamp()))
    # time updated
    updated_at = Column(Integer, default=int(datetime.now().timestamp()), onupdate=int(datetime.now().timestamp()))

    # @classmethod
    # # select tags for units
    # async def select_by_schedule(cls, schedule_ids: list, customer_ids: list = None, order_ids: list or set = None,
    #                              fields: list = None) -> list:
    #     # join
    #     j = join(CustomerOrders, Order, CustomerOrders.order_id == Order.id, isouter=True)
    #
    #     # set selected fields
    #     if not fields:
    #         fields = [CustomerOrders, Order]
    #
    #     # query to db
    #     query = select(fields)
    #
    #     # conditions
    #     # by tag_ids
    #     if order_ids:
    #         query = query.where(CustomerOrders.order_id == any_(order_ids))
    #     # by fleet_ids
    #     if schedule_ids:
    #         query = query.where(Order.schedule_id == any_(schedule_ids))
    #     # by unit_ids
    #     if customer_ids:
    #         query = query.where(CustomerOrders.customer_id == any_(customer_ids))
    #
    #     # add join
    #     query = query.select_from(j)
    #
    #     # return all records
    #     return await DBManager().query_fetch(query)