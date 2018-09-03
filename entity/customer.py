from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint

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
    email = Column(String(50), unique=True)
    # time created
    created_at = Column(Integer, default=int(datetime.now().timestamp()))
    # time updated
    updated_at = Column(Integer, default=int(datetime.now().timestamp()), onupdate=int(datetime.now().timestamp()))

    __table_args__ = (
        UniqueConstraint('email', 'phone'),
    )
