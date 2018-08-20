from sqlalchemy import Column, Integer, String, types, Boolean, ForeignKey, DateTime, DATETIME, UniqueConstraint
from datetime import datetime
from .base import Base, BaseEntity


# Entity Order
class SCHDetail(Base, BaseEntity):
    __tablename__ = 'SCHDetails'

    # id
    id = Column(Integer, primary_key=True)
    # order time
    time = Column(Integer, nullable=False)
    # time description
    description = Column(String(length=200))
    # members count
    members = Column(Integer, default=1, nullable=False)
    # schedule
    schedule_id = Column(Integer, nullable=False)
    # time created
    created_at = Column(Integer, default=int(datetime.now().timestamp()))
    # time updated
    updated_at = Column(Integer, default=int(datetime.now().timestamp()), onupdate=int(datetime.now().timestamp()))
