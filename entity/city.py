from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, DATETIME, UniqueConstraint
from datetime import datetime
from .base import Base, BaseEntity


# Entity City
class City(Base, BaseEntity):
    __tablename__ = 'Cities'

    # id
    id = Column(Integer, primary_key=True)
    # City name
    label = Column(String(200), nullable=False)
    # time created
    created_at = Column(Integer, default=int(datetime.now().timestamp()))
    # time updated
    updated_at = Column(Integer, default=int(datetime.now().timestamp()), onupdate=int(datetime.now().timestamp()))

