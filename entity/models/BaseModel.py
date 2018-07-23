from core.exceptions import IncorrectParamsException
from marshmallow import Schema, fields, UnmarshalResult
from abc import ABCMeta, abstractmethod
from sqlalchemy.sql import any_


# abstract class: business-model by entity
class BaseModel:
    __metaclass__ = ABCMeta

    def __init__(self, entity_cls, all_fields: set or list=set(), select_fields: set or list=set()):
        # class entity
        self.entity_cls = entity_cls
        # all fields by getting from API
        self.all_fields = all_fields

        # set selected fields
        if select_fields:
            # if fields from request - validate
            if not self.validate_fields(select_fields):
                # if not validate - Exception
                exc = IncorrectParamsException('Not validate get-params')
                exc.add_error('fields', 'Not validate')
                raise exc
            # and set
            self.select_fields = select_fields
        # if not selected fields - all
        else:
            self.select_fields = set(self.all_fields)

    @abstractmethod
    def _get_create_schema(self) -> Schema:
        """
        Schema for create Entity
        :return: Schema
        """

    @abstractmethod
    def _get_update_schema(self) -> Schema:
        """
        Schema for update Entity
        :return: Schema
        """

    # validate fields from request and this
    def validate_fields(self, _fields) -> bool:
        for field_name in _fields:
            if field_name not in self.all_fields:
                return False
        return True

    # standard error item
    def get_error_item(self, selector: str, reason: str, value=None, **kwargs) -> dict:
        """
        :param selector: str. Selector/field of error
        :param reason: str. Reason of error
        :param value: value. Value/id/selector-value
        :param kwargs: other params - added ro dict error
        :return: dict. Item error
        """
        # default dict
        error = dict(
            selector=selector,
            reason=reason
        )
        # add value
        if value:
            error['value'] = value
        # add other fields
        if kwargs:
            for i in kwargs:
                error[i] = kwargs[i]
        return error

    # standard result item
    def get_result_item(self, data, fields) -> dict:
        """
        :param data: dict or asyncpgsa.record.Record
        :param fields: list or set
        :return: dict
        """
        result = {}
        # if dict
        if isinstance(data, dict):
            for field in fields:
                result[field] = data.get(field, None)
        # if Record
        else:
            for field in fields:
                try:
                    result[field] = data[field]
                except:
                    result[field] = None
        return result

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
    async def get_base_condition(self) -> list:
        return []

    # GET Entities - default method (by ids)
    async def get_entities(self, ids: list, filter_name: str=None, **kwargs) -> tuple:
        # result success
        result = []
        # result errors
        errors = []

        # conditions by select entities
        conditions = await self.get_base_condition()

        # condition by selector ids/all
        if ids:
            #TODO check permissions for user
            # add allowed_ids in conditions
            conditions.append(self.entity_cls.id == any_(ids))

        # condition by selector name
        if filter_name:
            conditions.append(self.entity_cls.label.contains(filter_name))

        # select by conditions
        records = await self.entity_cls.select_where(
            str_fields=self.select_fields,
            conditions=conditions
        )

        # generate result list
        [result.append(self.get_result_item(record, self.select_fields)) for record in records]

        return result, errors

    # CREATE Entity - default method
    async def create_entity(self, data: dict, **kwargs) -> tuple:
        # result success
        result = {}
        # result errors
        error = {}

        # validate data
        vd = (self._get_create_schema()).load(data)

        # if error return error-item
        if vd.errors:
            error = self.get_error_item('data', 'No valid data')
        # create record
        else:
            # create and get result
            new_entity_data = await self.entity_cls.create(values=vd.data, return_fields=self.select_fields)
            # add to result
            if new_entity_data:
                result = self.get_result_item(new_entity_data, self.select_fields)
            else:
                error = self.get_error_item('Operation create', 'Error on execute query')

        return result, error

    # UPDATE Entity - default method
    async def update_entity(self, data: dict, **kwargs) -> tuple:
        # results success
        result = []
        # result errors
        error = []

        # validate data
        vd = (self._get_update_schema()).load(data)

        # if error return error-item
        if vd.errors:
            error = self.get_error_item('data', 'No valid data')
        # create record
        else:
            # update and get result
            updated_data = await self.entity_cls.update(vd.data.pop('id', None), vd.data, return_fields=self.select_fields)
            # add to result
            if updated_data:
                result = self.get_result_item(updated_data, self.select_fields)
            else:
                error = self.get_error_item('Operation update', 'Error on execute query')

        return result, error

    # DELETE Entity - default method
    async def delete_entity(self, id: int, **kwargs) -> tuple:
        # results success
        result = []
        # result errors
        errors = []

        # condition by selector id
        if id:
            # TODO check permissions for entity & session user
            # find item in database
            entity_item = await self.entity_cls.select_where(
                cls_fields=[self.entity_cls.id],
                conditions=[
                    self.entity_cls.id == id
                ]
            )
            # if item finded & has permissions delete it
            if entity_item:
                if await self.entity_cls.delete_by_id(id):
                    result.append(id)
                else:
                    errors.append(self.get_error_item(selector='id', reason='Access denied', value=id))
            else:
                errors.append(self.get_error_item(selector='id', reason='Not found', value=id))
        else:
            errors = self.get_error_item('id', 'No valid data')

        return result, errors
