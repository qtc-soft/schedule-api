from aiohttp import web
import ujson
from abc import ABCMeta, abstractmethod

from core.exceptions import IncorrectParamsException
from core.web_view import DefaultMethodsImpl
from entity.models.UserModel import UserModel
from entity.models.AuthModel import AuthModel

from marshmallow import Schema, fields

from aiohttp import web
import aiohttp_jinja2


# index-page
class ApiHelper(web.View):
    @aiohttp_jinja2.template('index.html')
    async def get(self):
        return {'title': 'Schedule API'}

# Class View
class Login(DefaultMethodsImpl):
    __metaclass__ = ABCMeta

    is_auth = False

    def get_model(self):
        return AuthModel()

    # validate data: data is list
    def validate_body_params(self, data) -> dict:
        # schema for default get-params
        class LoginSchema(Schema):
            login = fields.String(required=True)
            password = fields.String(required=True)

        # validate
        valid_data = LoginSchema().load(data)

        # if errors
        if valid_data.errors:
            # error
            err = IncorrectParamsException('Invalid login-data')
            # calc errors
            for field_name in valid_data.errors:
                for err_msg in valid_data.errors[field_name]:
                    err.add_error(selector=field_name, reason=err_msg)
            # return error
            raise err

        # return validate data
        return valid_data.data

    # HTTP: POST
    async def post(self):
        # data from request.body
        body_data = await self.get_body_and_validate()
        # model.login
        data = await (self.get_model()).login(login=body_data['login'], password=body_data['password'])

        # json-response
        resp = web.json_response()
        # status 200 or 403
        if data:
            resp.body = ujson.dumps(dict(
                result=data.__dict__
            ))
        else:
            resp.set_status(status=403, reason='Access denied..')

        return resp

# Class View
class Logout(DefaultMethodsImpl):
    __metaclass__ = ABCMeta

    is_auth = False

    def get_model(self):
        return AuthModel()

    # HTTP: POST
    async def post(self):
        # model.logout
        sid = self.request.headers.get('X-AccessToken')
        result = (self.get_model()).logout(sid) if sid else True

        # json-response
        resp = web.json_response(data=dict(result=[], errors=[]))
        # status 200 or 500
        if result:
            resp.set_status(status=200, reason='Success')
        else:
            resp.set_status(status=500, reason='Error operation logout')

        return resp


# schema for default get-params
class UsersMethodGetParamsSchema(Schema):
    ids = fields.List(fields.Integer())
    fields = fields.List(fields.String())

# Class View
class User(DefaultMethodsImpl):
    @property
    # list params for generate from str (,) to list
    def _def_params_names(self) -> tuple:
        return self.KEY_API_IDS, 'fields'

    @property
    # schema for validate def params
    def _params_schema(self) -> Schema:
        return UsersMethodGetParamsSchema()

    # get business-account
    def get_model(self):
        return UserModel(select_fields=self.request_def_params['fields'])

    # HTTP: GET
    async def get(self):
        # get models
        data = await (self.get_model()).get_entities(
            ids=self.request_def_params['ids'],
            filter_name=self.request.rel_url.query.get('name', None)
        )

        return web.json_response(data=dict(result=data[0], errors=data[1]))