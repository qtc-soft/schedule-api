"""
    Extensions for controllers
"""

import asyncio
import json

from aiohttp import web
from marshmallow import Schema, fields, UnmarshalResult
from .exceptions import IncorrectParamsException

from abc import ABCMeta, abstractmethod


# schema for default get-params
class DefParamsSchema(Schema):
    ids = fields.List(fields.Integer())
    fields = fields.List(fields.String())


# View-class for extended public_api
class ExtendedApiView(web.View):
    # const name param ids
    KEY_API_IDS = 'ids'
    # const select_all
    KEY_API_SELECT_ALL = 'all'

    # init function
    def __init__(self, request):
        super().__init__(request)
        # default get params
        self._def_request_params = None

    @property
    # list params for generate from str (,) to list
    def _def_params_names(self) -> tuple:
        return self.KEY_API_IDS, 'fields', 'label', 'name', 'description'

    @property
    # schema for validate def params
    def _params_schema(self) -> Schema:
        return DefParamsSchema()

    # apply schema, validate def params
    def _apply_params_schema(self, params: dict) -> UnmarshalResult:
        return self._params_schema.load(params)

    # generate get-params by _params_to_list
    def _get_def_request_params(self):
        #  result get-params
        params = {}
        # get def params
        for param_name in self._def_params_names:
            # if isset param in shema
            if param_name in self._params_schema.fields:
                # get-param by name
                p = self.request.match_info.get(param_name, '') or self.request.rel_url.query.get(param_name, '')
                # if param = all
                if p == self.KEY_API_SELECT_ALL:
                    params[param_name] = []
                else:
                    # calc param by shema.type (list or not)
                    if type(self._params_schema.fields[param_name]) == fields.List:
                        params[param_name] = p.split(',') if p else []
                    elif p:
                        params[param_name] = p

        # apply schema
        params_loaded = self._apply_params_schema(params)
        # if not validate
        if params_loaded.errors:
            # list errors
            errors = []
            # get validate-errors and write to dict errors
            for field_name in params_loaded.errors:
                for field_err_pos in params_loaded.errors[field_name]:
                    errors.append(dict(
                        selector=field_name,
                        reason=params_loaded.errors[field_name][field_err_pos][0] if isinstance(params_loaded.errors[field_name][field_err_pos], list) else params_loaded.errors[field_name][field_err_pos],
                        position=field_err_pos
                    ))

            # exception "not validate"
            raise IncorrectParamsException(msg='Incorrect param: {}'.format(params_loaded.errors, errors), errors=errors)

        # return dict by params_names
        return params_loaded.data

    @property
    # request def params getter
    def request_def_params(self) -> dict:
        if not self._def_request_params:
            self._def_request_params = self._get_def_request_params()
        return self._def_request_params

    # return data from request.post
    async def get_body_data(self):
        return await self.request.json() if self.request.can_read_body else {}

    # validate data: data is list
    def validate_body_params(self, data):
        if not isinstance(data, list):
            # exception
            raise IncorrectParamsException('Incorrect params in body', [dict(selector='body', reason='Expected: list')])

    # get data from body and validate
    async def get_body_and_validate(self) -> list:
        # get data (list) from body
        body_data = await self.get_body_data()
        # validate body_data
        self.validate_body_params(body_data)

        return body_data


# func-callback by finished Task
def task_finished_callback(task: asyncio.Task, res: list, err: list):
    # get task-result
    task_result = task.result()
    # if result
    if task_result[0]:
        if isinstance(task_result[0], list):
            res.extend(task_result[0])
        else:
            res.append(task_result[0])
    # if errors
    if task_result[1]:
        if isinstance(task_result[1], list):
            err.extend(task_result[1])
        else:
            err.append(task_result[1])


# abstract class: default implementation API-methods
class DefaultMethodsImpl(ExtendedApiView):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_model(self):
        """
        get business-model
        use get-param 'fields' (self.request_def_params['fields']) to create a model
        """

    # HTTP: GET
    async def get(self):
        # get-param 'fields' - used to create a model

        data = await (self.get_model()).get_entities()

        # return json-response
        return web.json_response(data=dict(result=data[0], errors=data[1]))

    # HTTP: POST
    async def post(self):
        # get data from body and validate
        body_data = await self.get_body_and_validate()

        # create model
        model = self.get_model()

        # result vars
        result = []
        errors = []

        # get event loop
        loop = asyncio.get_event_loop()

        # list tasks
        tasks = []
        # create Tasks
        for item in body_data:
            # create coroutine
            coro = model.create_entity(
                data=item
            )
            # create Task by coroutine
            task = loop.create_task(coro)
            # add callback by finished
            task.add_done_callback(lambda task: task_finished_callback(task=task, res=result, err=errors))
            # add to list tasks
            tasks.append(task)

        # wait tasks create Fleets
        await asyncio.wait(tasks)

        # return json-response
        return web.json_response(data=dict(result=result, errors=errors))

    # HTTP: PUT
    async def put(self):
        # get data from body and validate
        body_data = await self.get_body_and_validate()

        # Fleet model
        model = self.get_model()

        # result vars
        result = []
        errors = []

        # get event loop
        loop = asyncio.get_event_loop()

        # list tasks
        tasks = []
        # create Tasks
        for item in body_data:
            # create coroutine
            coro = model.update_entity(
                data=item,
            )
            # create Task by coroutine
            task = loop.create_task(coro)
            # add callback by finished
            task.add_done_callback(lambda task: task_finished_callback(task=task, res=result, err=errors))
            # add to list tasks
            tasks.append(task)

        # wait tasks update
        await asyncio.wait(tasks)

        # return json-response
        return web.json_response(data=dict(result=result, errors=errors))

    # HTTP: DELETE
    async def delete(self):
        # get ids from request
        ids = self.request_def_params['ids']

        # create model
        model = self.get_model()

        # result vars
        result = []
        errors = []

        # get event loop
        loop = asyncio.get_event_loop()

        # list tasks
        tasks = []
        # create Tasks
        for id in ids:
            # create coroutine
            coro = model.delete_entity(
                id=id
            )
            # create Task by coroutine
            task = loop.create_task(coro)
            # add callback by finished
            task.add_done_callback(lambda task: task_finished_callback(task=task, res=result, err=errors))
            # add to list tasks
            tasks.append(task)

        # wait tasks update
        await asyncio.wait(tasks)

        # return json-response
        return web.json_response(data=dict(result=result, errors=errors))
