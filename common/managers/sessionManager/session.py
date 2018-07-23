from settings import logger
from abc import ABCMeta, abstractmethod, abstractproperty, abstractclassmethod
from settings import *


# from marshmallow import Schema, fields, UnmarshalResult
# TODO: Add validate data for create Session
# schema for validate Entity for generate Session
# class DefSchema(Schema):
#     name = fields.String(required=True)
#     id = fields.Integer(required=True)


# base Session
class Session:
    __slots__ = 'name', 'id', 'sid', 'email', 'description'

    # load data from dict/object or kwargs
    def __init__(self, data: dict={}, **kwargs):
        # init object
        super().__init__()
        # int
        self.id = None
        # str
        self.name = None
        # str
        self.email = None
        # str
        self.description = None
        # str
        self.sid = None

        # set attrs from data-dict
        if data:
            self.load_dict(data)
        # set attrs by params
        if kwargs:
            self.load_dict(kwargs)

    # load attributes from dict
    def load_dict(self, data: dict):
        for field in data:
            try:
                getattr(self, field)
                self.__setattr__(field, data[field])
            except:
                pass

    def __bool__(self):
        return True if self.sid else False

    @property
    def __dict__(self) -> dict:
        return dict(
            id=self.id,
            name=self.name,
            sid=self.sid,
            email=self.email,
            description=self.description
        )

    def __str__(self):
        return 'Session {}. id={}, name={}, sid={}'.format(id(self), self.id, self.name, self.sid)