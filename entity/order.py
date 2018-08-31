from sqlalchemy import Column, Integer, String, types, Boolean, ForeignKey, DateTime, DATETIME, UniqueConstraint, Enum
from datetime import datetime
from .base import Base, BaseEntity

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
    schedule_id = Column(Integer, ForeignKey('Schedule.id'))
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
