from sqlalchemy import Column, Integer, String, types, Boolean, ForeignKey, DateTime, DATETIME, UniqueConstraint
from datetime import datetime
from .base import Base, BaseEntity
from hashlib import md5


# Entity Category
class User(Base, BaseEntity):
    __tablename__ = 'Users'

    # id
    id = Column(Integer, primary_key=True)
    # name User
    name = Column(String(length=100))
    # organization
    organization = Column(String(length=200))
    # description
    description = Column(String(length=200))
    # login, user can enter to system from login, phone or mail
    login = Column(String(length=100), nullable=False, unique=True)
    # password
    password = Column(String(100), nullable=False)
    # email
    email = Column(String(50), nullable=False)
    # confirm email value
    email_confirm = Column(Boolean, default=False)
    # phone
    phone = Column(String(20), unique=True, nullable=False)
    # confirm phone value
    phone_confirm = Column(Boolean, default=False)
    # Country id
    country_id = Column(Integer, ForeignKey('Countries.id'))
    # City id
    city_id = Column(Integer, ForeignKey('Cities.id'))
    # address
    address = Column(String(length=200))
    # mail agreement
    mail_agreement = Column(Boolean, default=True)
    # access flags, for block set 0
    flags = Column(Integer, default=1)
    # user settings
    data = Column(types.JSON)
    # time created
    created_at = Column(Integer, default=int(datetime.now().timestamp()))
    # time updated
    updated_at = Column(Integer, default=int(datetime.now().timestamp()), onupdate=int(datetime.now().timestamp()))

    __table_args__ = (
        UniqueConstraint('login', 'email'),
    )

    @classmethod
    # encrypt (for password)
    def p_encrypt(cls, val: str) -> str:
        return md5(val.encode('utf-8')).hexdigest()


# Entity UserSchedule
class UserSchedule(Base, BaseEntity):
    __tablename__ = 'UserSchedules'

    # id
    id = Column(Integer, primary_key=True)
    # User id
    user_id = Column(Integer, ForeignKey('Users.id'), nullable=False)
    # Schedule id
    schedule_id = Column(Integer, ForeignKey('Schedules.id'), nullable=False)

    __table_args__ = (
        # unique user & schedule id
        UniqueConstraint('user_id', 'schedule_id'),
    )