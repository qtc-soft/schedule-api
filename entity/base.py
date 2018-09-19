from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import select, update, delete, insert, \
    any_, \
    elements
from asyncpg.exceptions import UniqueViolationError

from settings import logger
from common.managers.dbManager import DBManager

Base = declarative_base()


# BaseEntity for Entity
class BaseEntity(object):
    # properties to dict
    def to_dict(self) -> dict:
        return self.__dict__

    @classmethod
    # get fields-records from DB by condition
    async def select_where(cls, cls_fields: set=(), str_fields: set=(), conditions: list=None):
        # query = select([cls.__getattribute__(cls, field) for field in fields] if fields else [cls])

        if not cls_fields and not str_fields:
            fields = [cls]
        else:
            fields = list(cls_fields) if cls_fields else []
            if str_fields:
                for field in str_fields:
                    try:
                        fields.append(cls.__getattribute__(cls, field))
                    except:
                        logger.debug('Field {} not found in cls {}'.format(field, cls))

        query = select(fields if fields else [cls])

        # add conditions
        if conditions:
            for condition in conditions:
                if isinstance(condition, elements.ColumnElement):
                    query = query.where(condition)

        return await DBManager().query_fetch(query)

    @classmethod
    # get all records from DB
    async def select_all(cls):
        return await cls.select_all_by_fields([cls])

    @classmethod
    # get all records by fields from DB
    async def select_all_by_fields(cls, fields: list=list()):
        if not fields or len(fields) == 0:
            fields = [cls]
        return await DBManager().query_fetch(select(fields))

    @classmethod
    # select record from DB by record_id
    async def select_by_id(cls, model_id: int):
        return await DBManager().query_fetchrow(select([cls]).where(cls.id == model_id))

    @classmethod
    # select records from DB by record_ids
    async def select_by_ids(cls, model_ids: list or set):
        return await DBManager().query_fetch(select([cls]).where(cls.id == any_(model_ids)))

    @classmethod
    # insert into table
    async def create(cls, values: dict, return_fields: list or set=None) -> {int or bool, str}:
        # message/error
        msg = ''
        # list returning-fields
        if not return_fields:
            return_fields = ['id']
        # create query and execute
        try:
            # result create
            rc = await DBManager().query_fetchrow(
                insert(cls).values(values).returning(*map(lambda field: cls.__getattribute__(cls, field), return_fields))
            )
        except UniqueViolationError as e:
            rc, msg = False, 'Record already exists'
        except Exception as e:
            logger.error('common.entity.baseEntity.BaseEntity#create: {}'.format(e))
            rc = False

        return rc, msg

    @classmethod
    # update record in db by entity.id
    async def update(cls, values: dict, rec_id: int=None, conditions: list=[], return_fields: list or set=None) -> {dict or bool, str}:
        # message/error
        msg = ''
        # result update
        ru = False
        # add condition by id
        if rec_id:
            conditions.append(cls.id == rec_id)
        # list returning-fields
        if not return_fields:
            return_fields = {'id'}
        # create and execute query
        try:
            # query to db
            query = update(cls).values(values).returning(*map(lambda field: cls.__getattribute__(cls, field), return_fields))
            for condition in conditions:
                if isinstance(condition, elements.ColumnElement):
                    query = query.where(condition)

            ru = await DBManager().query_fetchrow(query)
        except Exception as e:
            logger.error('common.entity.baseEntity.BaseEntity#update: {}'.format(e))
            msg = 'Error update record'

        return ru, msg

    @classmethod
    # update records in db by conditions
    async def update_by_conditions(cls, values: dict, conditions: list=None, return_fields: list or set=None, force: bool=False) -> dict or bool:
        # result update
        ru = False
        if not conditions and force:
            conditions = []
        if conditions:
            # create query
            query = update(cls).values(values)
            for condition in conditions:
                query = query.where(condition)

            # list returning-fields
            if not return_fields:
                return_fields = ['id']

            # execute query
            try:
                ru = await DBManager().query_fetch(
                    query.returning(*map(lambda field: cls.__getattribute__(cls, field), return_fields))
                )
            except Exception as e:
                logger.error('common.entity.baseEntity.BaseEntity#update: {}'.format(e))

        return ru

    @classmethod
    # delete record from DB by record_id
    async def delete_by_id(cls, rec_id: int):
        return await DBManager().query_execute(delete(cls).where(cls.id == rec_id))
