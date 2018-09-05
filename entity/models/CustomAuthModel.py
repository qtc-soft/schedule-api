from common.managers.sessionManager import SessionManager

from entity.customer import Customer
from entity.models.CustomerModel import CustomerModel


# business-model by authentification Customer
class CustomAuthModel:
    # login, return session
    async def login(self, login: str, password: str):
        # result bool or session
        result = False
        # search Customer
        u = await Customer.select_where(
            cls_fields=[Customer.id, Customer.name, Customer.login, Customer.email, Customer.phone, Customer.email_confirm, Customer.phone_confirm, Customer.flags],
            conditions=[Customer.login == login, Customer.password == Customer.p_encrypt(password), Customer.email_confirm == True or Customer.phone_confirm == True]
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
            result, errors = await um.create_entity(data)

        return result, errors

    # logout
    def logout(self, sid: str) -> bool:
        # delete
        SessionManager().del_session(sid)

        return True