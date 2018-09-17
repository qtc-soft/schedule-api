from common.managers.sessionManager import SessionManager

from entity.customer import Customer
from entity.models.CustomerModel import CustomerModel

from sqlalchemy.sql import or_


# business-model by authentification Customer
class CustomAuthModel:
    # login, return session
    async def login(self, login: str, password: str):
        # result bool or session
        result = False
        # search Customer
        u = await Customer.select_where(
            cls_fields=[Customer.id, Customer.name, Customer.login, Customer.email, Customer.phone, Customer.email_confirm, Customer.phone_confirm, Customer.flags],
            conditions=[Customer.login == login, Customer.password == Customer.p_encrypt(password), or_(not Customer.email_confirm, not Customer.phone_confirm)]
        )
        # if isset
        if u:
            session_data = SessionManager().generate_session(data=dict(u[0]))
            result = dict(sid=session_data.sid, name=session_data.name, login=session_data.login, email=session_data.email, phone=session_data.phone)

        return result

    # registration, return new user
    async def registration(self, data: dict):
        # result vars
        result = []
        errors = []

        um = CustomerModel()

        # search Customer
        entityWithLogin = await Customer.select_where(
            cls_fields=[Customer.id, Customer.login, Customer.email, Customer.phone],
            conditions=[Customer.login == data["login"]]
        )
        entityWithEmail = await Customer.select_where(
            cls_fields=[Customer.id, Customer.login, Customer.email, Customer.phone],
            conditions=[Customer.email == data["email"]]
        )
        entityWithPhone = await Customer.select_where(
            cls_fields=[Customer.id, Customer.login, Customer.email, Customer.phone],
            conditions=[Customer.phone == data["phone"]]
        )
        # if item finded & has permissions delete it
        if entityWithLogin:
            errors.append(um.get_error_item(selector='login', reason='Account with such login is exists', value=data["login"]))
        elif entityWithEmail:
            errors.append(um.get_error_item(selector='email', reason='Account with such email is exists', value=data["email"]))
        elif entityWithPhone:
            errors.append(um.get_error_item(selector='phone', reason='Account with such phone is exists', value=data["phone"]))
        else:
            # remove confirmed during registration
            data.pop('email_confirm')
            data.pop('phone_confirm')
            # create user
            user_data, errors = await um.create_entity(data)
            #  config response
            if user_data:
                result = dict(id=user_data['id'], name=user_data['name'],
                              login=user_data['login'], email=user_data['email'], phone=user_data['phone'])
            else:
                result = False

        return result, errors

    # confirm email
    async def confirm_email(self, key: str) -> bool:
        # result bool or session
        result = False

        # search User
        u = await Customer.select_where(
            cls_fields={Customer.id, Customer.name, Customer.login, Customer.email, Customer.phone, Customer.email_confirm,
                        Customer.phone_confirm,
                        Customer.flags},
            conditions=[Customer.email_confirm == key]
        )
        # if isset
        if u:
            # delete key from DB
            result = await Customer.update(
                rec_id=u[0]['id'],
                values=dict(email_confirm='')
            )
        return result

    # logout
    def logout(self, sid: str) -> bool:
        # delete
        SessionManager().del_session(sid)

        return True