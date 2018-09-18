from core.exceptions import IncorrectParamsException
from marshmallow import Schema, fields, UnmarshalResult
from abc import ABCMeta, abstractmethod
from sqlalchemy.sql import any_

from core.utils import calc_errors_from_vd, get_error_item, get_result_item, validate_by_schema


# abstract class: business-model by entity
class BaseModel(metaclass=ABCMeta):
    def __init__(self, entity_cls, all_fields: set or list=set(), select_fields: set or list=set(), **kwargs):
        # class entity
        self.entity_cls = entity_cls
        # all fields by getting from API
        self.all_fields = all_fields

        # set selected fields
        if select_fields:
            # if fields from request - validate
            if not self.validate_select_fields(select_fields):
                # if not validate - Exception
                exc = IncorrectParamsException('Not validate get-params')
                exc.add_error('fields', 'Not validate')
                raise exc
            # and set
            self.select_fields = set(select_fields)
        # if not selected fields - all
        else:
            self.select_fields = set(self.all_fields)

        # base conditions for all requests to db
        self._base_conditions = kwargs.get('conditions', [])

    @classmethod
    @abstractmethod
    def _get_create_schema(cls) -> Schema:
        """
        Schema for create Entity
        :return: Schema
        """

    @classmethod
    @abstractmethod
    def _get_update_schema(cls) -> Schema:
        """
        Schema for update Entity
        :return: Schema
        """

    # validate fields from request and this
    def validate_select_fields(self, _fields) -> bool:
        for field_name in _fields:
            if field_name not in self.all_fields:
                return False
        return True

    # standard error item
    def get_error_item(self, selector: str='', value=None, reason: str='Not found', **kwargs) -> dict:
        return get_error_item(selector, value, reason, **kwargs)

    # calc errors from validate-data (errors) by UnmarshalResult
    def calc_errors_from_vd(self, errors: dict, data_on_validate: dict={}) -> list:
        return calc_errors_from_vd(errors, data_on_validate)

    # standard result item
    def get_result_item(self, data, fields) -> dict:
        return get_result_item(data, fields)

    # func for find 'allowed ids' and 'not found ids' in list items (Records)
    def get_allowed_ids_by_list(self, all_ids: list or set, items: list or set, field_value=None, field_name: str='tsp_id'):
        """
        :param all_ids: list. All ids by filter
        :param items: list(dict or Record)
        :param field_value: value for filter by field_name
        :param field_name: str. Name field for comparison
        :return: (list, list) (allowed_ids: list, errors: list)
        """
        # allowed ids
        allowed_ids = []
        # list errors
        errors = []
        # check ids
        for item in items:
            # remove from ids for select errors 'not found'
            all_ids.remove(item['id'])
            # check allowed if filter
            if field_name and field_value:
                # allowed if tsp_id = self.tsp_id
                if item[field_name] == field_value:
                    allowed_ids.append(item['id'])
                # else - add error access denied
                else:
                    errors.append(self.get_error_item(selector='id', reason='Access denied', value=item['id']))
            # or not check
            else:
                allowed_ids.append(item['id'])

        # add errors 'not found'
        [errors.append(self.get_error_item(selector='id', reason='Not found', value=val)) for val in all_ids]

        return allowed_ids, errors

    # base conditions by select entities
    async def _get_base_condition(self) -> list:
        return self._base_conditions

    # return conditions for query select/update/delete
    async def _calc_conditions(self, add_cond: list=None) -> list:
        c = await self._get_base_condition()
        if add_cond and isinstance(add_cond, list):
            c.extend(add_cond)
        return c

    # calc results/errors by records&ids
    def calc_result(self, records, ids, result: list, errors: list):
        # calc result list
        for record in records:
            result.append(self.get_result_item(record, self.select_fields))
            # if select by ids - remove item.if for check error-not-found
            if ids:
                ids.remove(record['id'])

        # calc errors
        if ids:
            for rec_id in ids:
                errors.append(self.get_error_item(selector='id', value=rec_id))

        return result, errors

    # GET Entities - default method (by ids), in kwargs may be conditions
    async def get_entities(self, ids: list, **kwargs) -> tuple:
        # result success
        result = []
        # result errors
        errors = []

        # conditions for query
        conditions = await self._calc_conditions(kwargs.get('conditions'))

        # select by conditions
        sel_fields = self.select_fields
        # check select by ids
        if ids:
            sel_fields.add('id')
            conditions.append(self.entity_cls.id == any_(ids))

        # query to db
        records = await self.entity_cls.select_where(
            str_fields=sel_fields,
            conditions=conditions
        )

        self.calc_result(records, ids, result, errors)

        return result, errors

    # validate dict by create-schema
    def validate_for_create(self, data):
        return validate_by_schema(self._get_create_schema(), data)

    # validate dict by update-schema
    def validate_for_update(self, data):
        return validate_by_schema(self._get_update_schema(), data)

    # CREATE Entity - default method
    async def create_entity(self, data: dict, validate: bool=True, **kwargs) -> {dict, list}:
        # result success
        result = {}
        # result errors
        errors = []

        # TODO: Add to v_data from kwargs or not??
        # validate-data
        if validate:
            v_data, errs = self.validate_for_create(data)
            if errs:
                errors.extend(errs)
        else:
            v_data = data

        # create record
        if not errors and v_data:
            # create and get result
            new_entity_data, msg = await self.entity_cls.create(values=v_data, return_fields=self.select_fields)
            # add to result
            if new_entity_data:
                result = self.get_result_item(new_entity_data, self.select_fields)
            else:
                errors.append(self.get_error_item(selector='data', value=data, reason=msg))

        return result, errors

    # UPDATE Entity - default method, in kwargs may be conditions
    async def update_entity(self, data: dict, validate=True, **kwargs) -> {dict, list}:
        # results success
        result = {}
        # result errors
        errors = []

        # TODO: Add to v_data from kwargs or not??
        # validate-data
        if validate:
            v_data, errs = self.validate_for_update(data)
            if errs:
                errors.extend(errs)
        else:
            v_data = data

        # create record
        if not errors and v_data:
            # conditions for query
            conditions = await self._calc_conditions(kwargs.get('conditions'))

            # update and get result
            updated_data, msg = await self.entity_cls.update(
                rec_id=v_data.pop('id', None),
                values=v_data,
                conditions=conditions,
                return_fields=self.select_fields
            )
            # add to result
            if updated_data:
                result = self.get_result_item(updated_data, self.select_fields)
            else:
                errors.append(self.get_error_item(value=data, reason='Error on execute query'))

        return result, errors

    # DELETE Entity - default method, in kwargs may be conditions
    async def delete_entity(self, obj_id: int, **kwargs) -> tuple:
        # results
        result, errors = [], []

        # condition by selector id
        if obj_id:
            # conditions for query
            conditions = await self._calc_conditions(kwargs.get('conditions'))
            conditions.append(self.entity_cls.id == obj_id)

            # TODO: Bad code! remove select-query
            # find item in database
            entity_item = await self.entity_cls.select_where(
                cls_fields=[self.entity_cls.id],
                conditions=conditions
            )
            # if item finded & has permissions delete it
            if entity_item:
                if await self.entity_cls.delete_by_id(obj_id):
                    result.append(obj_id)
                else:
                    errors.append(self.get_error_item(selector='id', reason='Access denied', value=obj_id))
            else:
                errors.append(self.get_error_item(selector='id', reason='Not found', value=obj_id))
        else:
            errors = self.get_error_item('id', 'No valid data')

        return result, errors
