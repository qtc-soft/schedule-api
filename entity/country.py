from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, DATETIME, UniqueConstraint
from datetime import datetime
from .base import Base, BaseEntity


# Entity Country
class Country(Base, BaseEntity):
    __tablename__ = 'Countries'

    # id
    id = Column(Integer, primary_key=True)
    # Country name
    label = Column(String(200), nullable=False)
    # time created
    created_at = Column(Integer, default=int(datetime.now().timestamp()))
    # time updated
    updated_at = Column(Integer, default=int(datetime.now().timestamp()), onupdate=int(datetime.now().timestamp()))

