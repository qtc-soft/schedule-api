import ujson
import aiohttp_jinja2
from aiohttp import web
from aiohttp.hdrs import METH_GET, METH_PUT, METH_POST, METH_DELETE
from marshmallow import Schema, fields

from core.exceptions import IncorrectParamsException
from core.web_view import DefaultMethodsImpl, ExtendedApiView, DefGETParamsSchema
from entity.models.UserModel import UserModel
from entity.models.AuthModel import AuthModel
from entity.models.CustomAuthModel import CustomAuthModel
from entity.models.ScheduleModel import ScheduleModel, ScheduleOnlineModel
from entity.models.ScheduleDetailModel import ScheduleDetailModel
from entity.models.OrderModel import OrderModel
from entity.models.CustomerModel import CustomerModel


# index-page
class ApiHelper(web.View):
    @aiohttp_jinja2.template('index.html')
    async def get(self):
        return {'title': 'Schedule API'}


# Class View
class UserRegistration(DefaultMethodsImpl):

    is_auth = False

    @classmethod
    def _get_params_schemas(cls) -> dict:
        return {}

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


class UserConfirmEmailParamsSchema(Schema):
    key = fields.String(12, required=True)


# Class View
class UserConfirmEmail(DefaultMethodsImpl):

    is_auth = False

    @classmethod
    def _get_params_schemas(cls) -> dict:
        r = DefaultMethodsImpl._get_params_schemas()
        r[METH_GET] = UserConfirmEmailParamsSchema()
        return r

    def get_model(self):
        return AuthModel()

    # HTTP: GET
    async def get(self):
        # model.confirm_email
        result = await (self.get_model()).confirm_email(key=self.request.rel_url.query.get('key', None))

        # json-response
        resp = web.json_response()
        # status 200 or 403
        if result:
            resp.body = ujson.dumps(dict(
                result=True
            ))
        else:
            resp.set_status(status=403, reason='Access denied..')

        return resp


# Class View
class UserLogin(DefaultMethodsImpl):

    is_auth = False

    @classmethod
    def _get_params_schemas(cls) -> dict:
        return {}

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
        result, error = await (self.get_model()).login(login=body_data['login'], password=body_data['password'])

        # json-response
        resp = web.json_response()
        # status 200 or 403
        if error:
            resp.set_status(status=403, reason=error)
        elif result:
            resp.body = ujson.dumps(dict(
                result=result
            ))
        else:
            resp.set_status(status=403, reason='Access denied..')

        return resp


# Class View
class UserLogout(DefaultMethodsImpl):

    is_auth = False

    @classmethod
    def _get_params_schemas(cls) -> dict:
        return {}

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

    @classmethod
    def _get_params_schemas(cls) -> dict:
        return {}

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

    @classmethod
    def _get_params_schemas(cls) -> dict:
        return {}

    def get_model(self):
        return CustomAuthModel()

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


class CustomConfirmEmailParamsSchema(Schema):
    key = fields.String(12, required=True)


# Class View
class CustomConfirmEmail(DefaultMethodsImpl):

    is_auth = False

    @classmethod
    def _get_params_schemas(cls) -> dict:
        r = DefaultMethodsImpl._get_params_schemas()
        r[METH_GET] = CustomConfirmEmailParamsSchema()
        return r

    def get_model(self):
        return CustomAuthModel()

    # HTTP: GET
    async def get(self):
        # model.confirm_email
        result = await (self.get_model()).confirm_email(key=self.request.rel_url.query.get('key', None))

        # json-response
        resp = web.json_response()
        # status 200 or 403
        if result:
            resp.body = ujson.dumps(dict(
                result=True
            ))
        else:
            resp.set_status(status=403, reason='Access denied..')

        return resp


# Class View
class CustomLogout(DefaultMethodsImpl):

    is_auth = False

    @classmethod
    def _get_params_schemas(cls) -> dict:
        return {}

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
class IsAuth (ExtendedApiView):
    @classmethod
    def _get_params_schemas(cls) -> dict:
        return {}

    async def post(self):
        # sid from header
        request_sid = self.request.headers.get('X-AccessToken')
        # return json-response
        return web.json_response(data=dict(result=[dict(access=bool(self.session.sid == request_sid))], errors=[]))


# Class View
class User(DefaultMethodsImpl):
    # get business-account
    def get_model(self) -> UserModel:
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
    # get business-account
    def get_model(self) -> ScheduleModel:
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
class ScheduleOnlineGetParamsSchema(DefGETParamsSchema):
    name = fields.String()


class ScheduleOnline(DefaultMethodsImpl):

    is_auth = False

    @classmethod
    def _get_params_schemas(cls) -> dict:
        r = DefaultMethodsImpl._get_params_schemas()
        r[METH_GET] = ScheduleOnlineGetParamsSchema()
        return r

    # get business-account
    def get_model(self) -> ScheduleOnlineModel:
        return ScheduleOnlineModel(select_fields=self.request_def_params['fields'])

    # HTTP: GET
    async def get(self):
        # get models
        data = await (self.get_model()).get_entities(
            ids=self.request_def_params['ids'],
            filter_name=self.request.rel_url.query.get('name', None)
        )

        return web.json_response(data=dict(result=data[0], errors=data[1]))


# schema for default get-params
class ScheduleDetailMethodGetParamsSchema(DefGETParamsSchema):
    schedules = fields.List(fields.Integer())


# Class View
class ScheduleDetail(DefaultMethodsImpl):
    @classmethod
    def _get_params_schemas(cls) -> dict:
        r = DefaultMethodsImpl._get_params_schemas()
        r[METH_GET] = ScheduleDetailMethodGetParamsSchema()
        return r

    # get business-account
    def get_model(self) -> ScheduleDetailModel:
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
class OrderMethodGetParamsSchema(DefGETParamsSchema):
    schedules = fields.List(fields.Integer())
    customers = fields.List(fields.Integer())
    status = fields.String()


# Class View
class Order(DefaultMethodsImpl):
    # schema for validate def params
    @classmethod
    def _get_params_schemas(cls) -> dict:
        r = DefaultMethodsImpl._get_params_schemas()
        r[METH_GET] = OrderMethodGetParamsSchema()
        return r

    # get business-account
    def get_model(self) -> OrderModel:
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
class CustomerMethodGetParamsSchema(DefGETParamsSchema):
    schedules = fields.List(fields.Integer())


# class View
class Customer(DefaultMethodsImpl):
    # schema for validate def params
    @classmethod
    def _get_params_schemas(cls) -> dict:
        r = DefaultMethodsImpl._get_params_schemas()
        r[METH_GET] = CustomerMethodGetParamsSchema()
        return r

    # get business-account
    def get_model(self) -> CustomerModel:
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