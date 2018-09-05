from sqlalchemy import Column, Integer, String, Boolean, types, UniqueConstraint

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
    # confirm phone value
    phone_confirm = Column(Boolean, default=False)
    # email
    email = Column(String(50), unique=True)
    # confirm phone value
    email_confirm = Column(Boolean, default=False)
    # mail agreement
    mail_agreement = Column(Boolean, default=True)
    # address
    address = Column(String(length=200))
    # access flags, for block set 0
    flags = Column(Integer, default=0)
    # user settings
    data = Column(types.JSON)
    # time created
    created_at = Column(Integer, default=int(datetime.now().timestamp()))
    # time updated
    updated_at = Column(Integer, default=int(datetime.now().timestamp()), onupdate=int(datetime.now().timestamp()))

    __table_args__ = (
        UniqueConstraint('email', 'phone'),
    )
