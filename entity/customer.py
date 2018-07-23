from sqlalchemy import Column, Integer, String, types, Boolean, ForeignKey, DateTime, DATETIME, UniqueConstraint
from datetime import datetime
from .base import Base, BaseEntity


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
        UniqueConstraint('phone'),
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