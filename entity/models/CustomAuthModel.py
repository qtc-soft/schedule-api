from entity.customer import Customer
from marshmallow import Schema, fields, validate
from sqlalchemy.sql import or_

from .BaseModel import BaseModel
from common.managers.sessionManager import SessionManager


# business-model by authentification Customer
class CustomerAuthModel(BaseModel):
    def __init__(self):
        """
        :param select_fields: set, list fields for result
        """
        super().__init__(
            entity_cls=Customer,
            all_fields=(
                'id',
                'name',
                'login',
                'email',
                'phone',
                'password',
                'email_confirm',
                'phone_confirm',
                'flags'
            )
        )

    # Schema for create
    @classmethod
    def _get_create_schema(self) -> Schema:
        # schema for create entity
        class CustomerLoginSchema(Schema):
            login = fields.String(required=True, validate=validate.Length(min=3, max=100))
            password = fields.String(required=True, validate=validate.Length(min=3, max=100))

        return CustomerLoginSchema()

    # Schema for update
    @classmethod
    def _get_update_schema(self) -> Schema:
        return Schema()

    # login, return session
    async def login(self, login: str, password: str):
        # result bool or session
        result = False
        error = False

        # search Customer
        u = await self.entity_cls.select_where(
            cls_fields=[self.entity_cls.id, self.entity_cls.login, self.entity_cls.password, self.entity_cls.email, self.entity_cls.email_confirm, self.entity_cls.phone, self.entity_cls.phone_confirm, self.entity_cls.flags],
            conditions=[self.entity_cls.login == login, self.entity_cls.password == self.entity_cls.p_encrypt(password), or_(self.entity_cls.email_confirm == '', self.entity_cls.phone_confirm == '')]
        )
        # if isset
        if u:
            if u[0]['email_confirm']:
                  error = 'Access denied.. Email not confirmed'
            else:
                # create session
                session_data = await SessionManager().generate_session(data=dict(u[0]))

                result = dict(id=session_data.id, sid=session_data.sid, login=session_data.login, email=session_data.email, phone=session_data.phone)

        return result, error

    # confirm email
    async def confirm_email(self, key: str) -> bool:
        # result bool or session
        result = False
        msg = ''

        # search Customer
        u = await Customer.select_where(
            cls_fields={Customer.id, Customer.name, Customer.login, Customer.email, Customer.phone, Customer.email_confirm, Customer.phone_confirm,
                        Customer.flags},
            conditions=[Customer.email_confirm == key]
        )
        # if isset
        if u:
            # delete key from DB
            result, msg = await super().update_entity(data=dict(id=u[0]['id'], email_confirm=''), validate=False)
        return result, msg

    # logout
    def logout(self, sid: str) -> bool:
        # delete
        SessionManager().del_session(sid)

        return True