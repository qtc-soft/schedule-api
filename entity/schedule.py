from sqlalchemy import Column, Integer, String, types, Boolean, ForeignKey, DateTime, DATETIME, UniqueConstraint
from datetime import datetime
from .base import Base, BaseEntity


# Entity Schedule
class Schedule(Base, BaseEntity):
    __tablename__ = 'Schedules'

    # id
    id = Column(Integer, primary_key=True)
    # schedule name - unique link
    name = Column(String(length=100), unique=True, nullable=False)
    #TODO take default data from user table
    # description
    description = Column(String(length=200))
    # email
    email = Column(String(50))
    # phone
    phone = Column(String(20))
    # creter
    creater_id = Column(Integer, ForeignKey('Users.id'), nullable=False)
    # Country id
    country_id = Column(Integer, ForeignKey('Countries.id'))
    # City id
    city_id = Column(Integer, ForeignKey('Cities.id'))
    # address
    address = Column(String(length=200))
    # access flags, for block set 0
    flags = Column(Integer, default=1)
    # some schedule settings, field for free data or schedule settings
    data = Column(types.JSON)
    # time created
    created_at = Column(Integer, default=int(datetime.now().timestamp()))
    # time updated
    updated_at = Column(Integer, default=int(datetime.now().timestamp()), onupdate=int(datetime.now().timestamp()))

    __table_args__ = (
        UniqueConstraint('name'),
    )
