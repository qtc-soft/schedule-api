"""
    Extensions for controllers
"""

import asyncio
from aiohttp import web, web_request
from aiohttp.hdrs import METH_GET, METH_PUT, METH_POST, METH_DELETE
from abc import ABCMeta, abstractmethod

from marshmallow import Schema, fields, UnmarshalResult
from .exceptions import IncorrectParamsException, AccessException

from common.managers.sessionManager import SessionManager
from common.managers.sessionManager import Session


# get auth-token from request
def get_auth_token_from_request(request: web.Request, param_name: str) -> str:
    return request.headers.get(param_name) or request.cookies.get(param_name)


# schema for default get-params
class DefParamsSchema(Schema):
    ids = fields.List(fields.Integer())
    fields = fields.List(fields.String())

# GET: schema for default get-params
class DefGETParamsSchema(Schema):
    ids = fields.List(fields.Integer(), default='all')
    fields = fields.List(fields.String())

# POST: schema for default get-params
class DefPOSTParamsSchema(Schema):
    fields = fields.List(fields.String())

# PUT: schema for default get-params
class DefPUTParamsSchema(Schema):
    fields = fields.List(fields.String())

# DELETE: schema for default get-params
class DefDELETEParamsSchema(Schema):
    ids = fields.List(fields.Integer())


# View-class for extended tsp_api
class ExtendedApiView(web.View, metaclass=ABCMeta):

    # const name param ids
    KEY_API_IDS = 'ids'
    # const select_all
    KEY_API_SELECT_ALL = 'all'
    # is authentification
    is_auth = True

    # init function
    def __init__(self, request: web_request.Request):
        super().__init__(request)
        # default get params
        self._def_request_params = None

        # authentification-Session
        self._session = self.session_storage.get_session_by_sid(get_auth_token_from_request(self.request, self.auth_header_name))

        if self.is_auth and not self._session:
            # error access denied
            raise AccessException('Access denied. Session is closed.')

    @classmethod
    # schemas for get-params by methods
    def _get_params_schemas(cls) -> dict:
        return {
            METH_GET: DefGETParamsSchema(),
            METH_POST: DefPOSTParamsSchema(),
            METH_PUT: DefPUTParamsSchema(),
            METH_DELETE: DefDELETEParamsSchema()
        }

    @property
    # Schema for self request-method
    def _get_params_schema(self) -> Schema or None:
        return self._get_params_schemas().get(self.request.method)

    # func for custom access control by session, check session
    def __access_control(self, *args, **kwargs) -> bool:
        return True

    @property
    # storage sessions
    def session_storage(self) -> SessionManager:
        return self.request.app.session_storage

    @property
    # Session, if is_auth = True
    def session(self) -> Session:
        return self._session

    # validate get-params, apply schema
    def _validate_get_params(self, params: dict) -> UnmarshalResult:
        return self._get_params_schema.load(params)

    # return get-params from request
    def _select_request_get_params(self):
        #  result get-params
        params = {}
        # get params
        for param_name in self._get_params_schema.fields:
            # param-value, select from request
            p = self.request.match_info.get(param_name, '') or self.request.rel_url.query.get(param_name, '')
            # if param = all
            if p == self.KEY_API_SELECT_ALL:
                params[param_name] = []
            else:
                # calc param by schema.type (list or not)
                if type(self._get_params_schema.fields[param_name]) == fields.List:
                    params[param_name] = p.split(',') if p else []
                elif p:
                    params[param_name] = p

        # validate
        params_loaded = self._validate_get_params(params)
        # if not validate
        if params_loaded.errors:
            # raise error
            raise IncorrectParamsException(msg='Incorrect get-params')

        # return dict by params_names
        return params_loaded.data

    @property
    # request def params getter
    def request_def_params(self) -> dict:
        if not self._request_get_params:
            self._request_get_params = self._select_request_get_params()
        return self._request_get_params

    @property
    # auth header name
    def auth_header_name(self) -> str:
        return self.request.app.auth_header_name

    # return data from request.post
    async def get_body_data(self):
        return await self.request.json() if self.request.can_read_body else {}

    # validate data: data is list
    def validate_body_params(self, data):
        if not isinstance(data, list):
            # exception
            raise IncorrectParamsException('Incorrect params in body', [dict(selector='body', reason='Expected: list')])
        return data

    # get data from body and validate
    async def get_body_and_validate(self):
        # get & validate body-data
        return self.validate_body_params(await self.get_body_data())


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
# this class extends ExtendedApiViewBase
class DefaultMethodsImpl(ExtendedApiView, metaclass=ABCMeta):
    @abstractmethod
    def get_model(self):
        """
        get business-model
        use get-param 'fields' (self.request_def_params['field']) to create a model
        """

    # HTTP: GET
    async def get(self):
        """
        ---
          tags:
          - MODEL
          summary: Help for MGate-API
          description: Get Fleets by ids
          produces:
          - application/json
          parameters:
          - in: path
            name: ids
            description: Model ids
            required: true
            default: all
            type: string
          - in: path
            name: fields
            description: List fields from Model
            required: false
            default: ''
            type: string
          responses:
            "200":
              description: successful operation
        """

        # get-param 'fields' - used to create a model

        data = await (self.get_model()).get_entities(
            ids=self.request_def_params['ids']
        )

        # return json-response
        return web.json_response(data=dict(result=data[0], errors=data[1]))

    # HTTP: POST, kwargs added to data for created items
    async def post(self, **kwargs):
        # get data from body and validate
        body_data = await self.get_body_and_validate()

        # create model
        model = self.get_model()

        # result vars
        result = []
        errors = []

        # list tasks
        tasks = []
        # create Tasks
        for item in body_data:
            # create coroutine
            coro = model.create_entity(
                data=item,
                **kwargs
            )
            # create Task by coroutine
            task = asyncio.create_task(coro)
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

        # list tasks
        tasks = []
        # create Tasks
        for item in body_data:
            # create coroutine
            coro = model.update_entity(
                data=item,
            )
            # create Task by coroutine
            task = asyncio.create_task(coro)
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

        # TODO: add msg to response: set ids
        if ids:
            # list tasks
            tasks = []
            # create Tasks
            for id in ids:
                # create coroutine
                coro = model.delete_entity(
                    obj_id=id
                )
                # create Task by coroutine
                task = asyncio.create_task(coro)
                # add callback by finished
                task.add_done_callback(lambda task: task_finished_callback(task=task, res=result, err=errors))
                # add to list tasks
                tasks.append(task)

            # wait tasks update
            await asyncio.wait(tasks)

        # return json-response
        return web.json_response(data=dict(result=result, errors=errors))
