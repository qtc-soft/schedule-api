from aiohttp import web
import ujson

from core.exceptions import IncorrectParamsException
from core.web_view import DefaultMethodsImpl
from entity.models.UserModel import UserModel
from entity.models.AuthModel import AuthModel
from entity.models.CustomAuthModel import CustomAuthModel
from entity.models.ScheduleModel import ScheduleModel, ScheduleOnlineModel
from entity.models.ScheduleDetailModel import ScheduleDetailModel
from entity.models.OrderModel import OrderModel
from entity.models.CustomerModel import CustomerModel

from marshmallow import Schema, fields

from aiohttp import web
import aiohttp_jinja2


# index-page
class ApiHelper(web.View):
    @aiohttp_jinja2.template('index.html')
    async def get(self):
        return {'title': 'Schedule API'}


# Class View
class UserRegistration(DefaultMethodsImpl):

    is_auth = False

    def get_model(self):
        return AuthModel()

    # validate data: data is list
    def validate_body_params(self, data) -> dict:
        # schema for default get-params
        class RegistrationSchema(Schema):
            login = fields.String(100, required=True)
            password = fields.String(100, required=True)
            email = fields.String(50, required=True)
            phone = fields.String(20, required=True)

        # validate
        valid_data = RegistrationSchema().load(data)

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
        result, errors = await (self.get_model()).registration(data=body_data)

        # return json-response
        return web.json_response(data=dict(result=result, errors=errors))


# Class View
class UserLogin(DefaultMethodsImpl):

    is_auth = False

    def get_model(self):
        return AuthModel()

    # validate data: data is list
    def validate_body_params(self, data) -> dict:
        # schema for default get-params
        class LoginSchema(Schema):
            login = fields.String(100, required=True)
            password = fields.String(100, required=True)

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
                result=data
            ))
        else:
            resp.set_status(status=403, reason='Access denied..')

        return resp


# Class View
class UserLogout(DefaultMethodsImpl):

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


# Class View
class CustomRegistration(DefaultMethodsImpl):

    is_auth = False

    def get_model(self):
        return CustomAuthModel()

    # validate data: data is list
    def validate_body_params(self, data) -> dict:
        # schema for default get-params
        class RegistrationSchema(Schema):
            login = fields.String(100, required=True)
            password = fields.String(100, required=True)
            email = fields.String(50, required=True)
            phone = fields.String(20, required=True)

        # validate
        valid_data = RegistrationSchema().load(data)

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
        result, errors = await (self.get_model()).registration(data=body_data)

        # return json-response
        return web.json_response(data=dict(result=result, errors=errors))


# Class View
class CustomLogin(DefaultMethodsImpl):

    is_auth = False

    def get_model(self):
        return AuthModel()

    # validate data: data is list
    def validate_body_params(self, data) -> dict:
        # schema for default get-params
        class LoginSchema(Schema):
            login = fields.String(100, required=True)
            password = fields.String(100, required=True)

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
                result=data
            ))
        else:
            resp.set_status(status=403, reason='Access denied..')

        return resp


# Class View
class CustomLogout(DefaultMethodsImpl):

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
class UserMethodGetParamsSchema(Schema):
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
        return UserMethodGetParamsSchema()

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


# Class View
class Schedule(DefaultMethodsImpl):
    @property
    # list params for generate from str (,) to list
    def _def_params_names(self) -> tuple:
        return self.KEY_API_IDS, 'fields', 'name'

    @property
    # schema for validate def params
    def _params_schema(self) -> Schema:
        return UserMethodGetParamsSchema()

    # get business-account
    def get_model(self):
        return ScheduleModel(select_fields=self.request_def_params['fields'], allowed_schedule_ids=self.session.schedule_ids, creater_id=self.session.id)

    # HTTP: GET
    async def get(self):
        # get models
        data = await (self.get_model()).get_entities(
            ids=self.request_def_params['ids'],
            filter_name=self.request.rel_url.query.get('name', None)
        )

        return web.json_response(data=dict(result=data[0], errors=data[1]))

    # HTTP: POST, only for User
    async def post(self):
        # json-response
        resp = await super().post()

        if self.session and self.session.id:
            # update session
            await self.session_storage.update_acl_by_acc_id(self.session.id)

        return resp


# schema for default get-params
class ScheduleOnlineGetParamsSchema(Schema):
    ids = fields.List(fields.Integer())
    name = fields.String()
    fields = fields.List(fields.String())


class ScheduleOnline(DefaultMethodsImpl):
    @property
    # list params for generate from str (,) to list
    def _def_params_names(self) -> tuple:
        return self.KEY_API_IDS, 'name', 'fields'

    @property
    # schema for validate def params
    def _params_schema(self) -> Schema:
        return ScheduleOnlineGetParamsSchema()

    # get business-account
    def get_model(self):
        return ScheduleOnlineModel(select_fields=self.request_def_params['fields'], creater_id=self.session.id)

    # HTTP: GET
    async def get(self):
        # get models
        data = await (self.get_model()).get_entities(
            ids=self.request_def_params['ids'],
            filter_name=self.request.rel_url.query.get('name', None)
        )

        return web.json_response(data=dict(result=data[0], errors=data[1]))


# schema for default get-params
class ScheduleDetailMethodGetParamsSchema(UserMethodGetParamsSchema):
    schedules = fields.List(fields.Integer())


# Class View
class ScheduleDetail(DefaultMethodsImpl):
    @property
    # list params for generate from str (,) to list
    def _def_params_names(self) -> tuple:
        return self.KEY_API_IDS, 'schedules', 'fields'

    @property
    # schema for validate def params
    def _params_schema(self) -> Schema:
        return ScheduleDetailMethodGetParamsSchema()

    # get business-account
    def get_model(self):
        return ScheduleDetailModel(select_fields=self.request_def_params['fields'], allowed_schedule_ids=self.session.schedule_ids, creater_id=self.session.id)

    # HTTP: GET
    async def get(self):
        # get tags by get-params
        data = await (self.get_model()).get_entities(
            ids=self.request_def_params['ids'],
            schedule_ids=self.request_def_params['schedules'],
        )

        return web.json_response(data=dict(result=data[0], errors=data[1]))


# schema for default get-params
class OrderMethodGetParamsSchema(UserMethodGetParamsSchema):
    schedules = fields.List(fields.Integer())
    customers = fields.List(fields.Integer())
    status = fields.String()


# Class View
class Order(DefaultMethodsImpl):
    @property
    # list params for generate from str (,) to list
    def _def_params_names(self) -> tuple:
        return self.KEY_API_IDS, 'status', 'schedules', 'customers'

    @property
    # schema for validate def params
    def _params_schema(self) -> Schema:
        return OrderMethodGetParamsSchema()

    # get business-account
    def get_model(self):
        return OrderModel(select_fields=self.request_def_params['fields'], allowed_schedule_ids=self.session.schedule_ids, creater_id=self.session.id)

    # HTTP: GET
    async def get(self):
        # get tags by get-params
        data = await (self.get_model()).get_entities(
            ids=self.request_def_params['ids'],
            filter_name=self.request.rel_url.query.get('name', None),
            schedule_ids=self.request_def_params['schedules'],
            customer_ids=self.request_def_params['customers'],
            status=self.request_def_params['status'],
        )

        return web.json_response(data=dict(result=data[0], errors=data[1]))


# schema for default get-params
class CustomerMethodGetParamsSchema(UserMethodGetParamsSchema):
    schedules = fields.List(fields.Integer())


# class View
class Customer(DefaultMethodsImpl):
    @property
    # list params for generate from str (,) to list
    def _def_params_names(self) -> tuple:
        return self.KEY_API_IDS, 'fields', 'schedules'

    @property
    # schema for validate def params
    def _params_schema(self) -> Schema:
        return CustomerMethodGetParamsSchema()

    # get business-account
    def get_model(self):
        return CustomerModel(select_fields=self.request_def_params['fields'], allowed_schedule_ids=self.session.schedule_ids, creater_id=self.session.id)

    # HTTP: GET
    async def get(self):
        # get tags by get-params
        data = await (self.get_model()).get_entities(
            ids=self.request_def_params['ids'],
            filter_name=self.request.rel_url.query.get('name', None),
            schedule_ids=self.request_def_params['schedules'],
        )

        return web.json_response(data=dict(result=data[0], errors=data[1]))