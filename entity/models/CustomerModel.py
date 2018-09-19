from sqlalchemy.sql import any_
from marshmallow import Schema, fields, validate
from .BaseModel import BaseModel
from entity.customer import Customer
from entity.order import Order


# business-model by entity User
class CustomerModel(BaseModel):
    def __init__(self, select_fields: set=set()):
        """
        :param select_fields: set, list fields for result
        """
        super().__init__(
            entity_cls=Customer,
            all_fields=(
                'id',
                'name',
                'description',
                'login',
                'password',
                'email',
                'phone',
                'country_id',
                'city_id',
                'address',
                'mail_agreement',
                'flags',
                'data'
            ),
            select_fields=select_fields
        )

    @classmethod
    def _get_create_schema(cls) -> Schema:
        # schema for create entity
        class CustomerCreateSchema(Schema):
            login = fields.String(required=True, validate=validate.Length(min=3, max=100))
            password = fields.String(required=True, validate=validate.Length(min=3, max=100))
            email = fields.Email(required=True)
            phone = fields.String(required=True)

        return CustomerCreateSchema()

    @classmethod
    def _get_update_schema(cls) -> Schema:
        # schema for update entity
        class CustomerUpdateSchema(Schema):
            id = fields.Integer(required=True)
            name = fields.String(length=100)
            description = fields.String(length=200)
            login = fields.String(validate=validate.Length(min=3, max=100))
            password = fields.String(validate=validate.Length(min=3, max=100))
            email = fields.Email()
            phone = fields.String(length=50)
            country_id = fields.Integer()
            city_id = fields.Integer()
            address = fields.String(length=200)
            mail_agreement = fields.Boolean(default=True)
            data = fields.Dict()
            flags = fields.Integer(default=1)

        return CustomerUpdateSchema()

    # GET Entity
    async def get_entities(self, ids: list, schedule_ids: set = None, filter_name: str = None) -> tuple:
        result = []
        errors = []

        # default filter customers only by ids in request
        allowed_customer_ids = ids

        # if need specific schedule data
        if schedule_ids:
            # condition by allowed Schedules
            allowed_schedule_ids = self.allowed_schedule_ids.intersection(schedule_ids)

            # get orders for some schedules
            order_items = await Order.select_where(
                cls_fields=[Order.id, Order.schedule_id],
                conditions=[Order.schedule_id == any_(allowed_schedule_ids)]
            )
            # get customer ids form orders
            allowed_customer_ids = [order_item['customer_id'] for order_item in order_items]
            if ids:
                allowed_customer_ids = allowed_customer_ids.intersection(ids)

        # base conditions
        conditions = await self._get_base_condition()

        # condition by selector ids
        if allowed_customer_ids:
            conditions.append(self.entity_cls.id == any_(allowed_customer_ids))

        # condition by selector name
        if filter_name:
            conditions.append(self.entity_cls.name.contains(filter_name))

        # select by conditions
        records = await self.entity_cls.select_where(
            str_fields=self.select_fields,
            conditions=conditions
        )

        self.calc_result(records, ids, result, errors)

        return result, errors

    # CREATE Entity, register new User
    async def create_entity(self, data: dict, **kwargs) -> tuple:
        # result vars
        result = []
        errors = []

        # search User
        entityWithLogin = await self.entity_cls.select_where(
            cls_fields=[self.entity_cls.id, self.entity_cls.login, self.entity_cls.email, self.entity_cls.phone],
            conditions=[self.entity_cls.login == data["login"]]
        )
        if not entityWithLogin:
            entityWithEmail = await self.entity_cls.select_where(
                cls_fields=[self.entity_cls.id, self.entity_cls.login, self.entity_cls.email, self.entity_cls.phone],
                conditions=[self.entity_cls.email == data["email"]]
            )
        else:
            entityWithEmail = False
        if not entityWithLogin and not entityWithEmail:
            entityWithPhone = await self.entity_cls.select_where(
                cls_fields=[self.entity_cls.id, self.entity_cls.login, self.entity_cls.email, self.entity_cls.phone],
                conditions=[self.entity_cls.phone == data["phone"]]
            )
        else:
            entityWithPhone = False
        # if item finded & has permissions delete it
        if entityWithLogin:
            errors.append(
                self.get_error_item(selector='login', reason='Account with such login is exists', value=data["login"]))
        elif entityWithEmail:
            errors.append(
                self.get_error_item(selector='email', reason='Account with such email is exists', value=data["email"]))
        elif entityWithPhone:
            errors.append(
                self.get_error_item(selector='phone', reason='Account with such phone is exists', value=data["phone"]))
        else:
            # remove confirmed during registration
            data.pop('email_confirm', None)
            data.pop('phone_confirm', None)
            # crypt code
            if data.get(self.entity_cls.password.name):
                data[self.entity_cls.password.name] = self.entity_cls.p_encrypt(data[self.entity_cls.password.name])
            # create user
            user_data, errors = await super().create_entity(data, **kwargs)
            #  config response
            if user_data:
                result = dict(id=user_data['id'], name=user_data['name'],
                              login=user_data['login'], email=user_data['email'], phone=user_data['phone'])

        return result, errors

    # UPDATE Entity
    async def update_entity(self, data: dict, **kwargs) -> tuple:
        # crypt code
        if data.get(self.entity_cls.password.name):
            data[self.entity_cls.password.name] = self.entity_cls.p_encrypt(data[self.entity_cls.password.name])
        # update
        result, errors = await super().update_entity(data, **kwargs)

        return result, errors
