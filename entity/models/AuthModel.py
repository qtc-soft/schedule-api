import smtplib
from common.managers.sessionManager import SessionManager

from entity.user import User
from entity.models.UserModel import UserModel

from sqlalchemy.sql import or_


# business-model by authentification User
class AuthModel:
    # login, return session
    async def login(self, login: str, password: str):
        # result bool or session
        result = False
        error = False

        # search User
        u = await User.select_where(
            cls_fields=[User.id, User.name, User.login, User.email, User.phone, User.email_confirm, User.phone_confirm, User.flags],
            conditions=[User.login == login, User.password == User.p_encrypt(password), or_(not User.email_confirm, not User.phone_confirm)]
        )
        # if isset
        if u:
            if u[0]['email_confirm']:
                  error = 'Access denied.. Email not confirmed'
            else:
                # create session
                session_data = await SessionManager().generate_session(data=dict(u[0]))

                result = dict(id=session_data.id, sid=session_data.sid, name=session_data.name, login=session_data.login, email=session_data.email, phone=session_data.phone)

        return result, error

    # registration, return new user
    async def registration(self, data: dict):
        # result vars
        result = []
        errors = []

        um = UserModel()

        # search User
        entityWithLogin = await User.select_where(
            cls_fields=[User.id, User.login, User.email, User.phone],
            conditions=[User.login == data["login"]]
        )
        entityWithEmail = await User.select_where(
            cls_fields=[User.id, User.login, User.email, User.phone],
            conditions=[User.email == data["email"]]
        )
        entityWithPhone = await User.select_where(
            cls_fields=[User.id, User.login, User.email, User.phone],
            conditions=[User.phone == data["phone"]]
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
            data.pop('email_confirm', None)
            data.pop('phone_confirm', None)
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
        u = await User.select_where(
            cls_fields={User.id, User.name, User.login, User.email, User.phone, User.email_confirm, User.phone_confirm,
                        User.flags},
            conditions=[User.email_confirm == key]
        )
        # if isset
        if u:
            # delete key from DB
            result = await User.update(
                rec_id=u[0]['id'],
                values=dict(email_confirm='')
            )
        return result

    # logout
    def logout(self, sid: str) -> bool:
        # delete
        SessionManager().del_session(sid)

        return True