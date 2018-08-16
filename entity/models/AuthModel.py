from common.managers.sessionManager import SessionManager

# TSP
from entity.user import User


# business-model by authentification User (from Fleet)
class AuthModel:
    # login, return session
    async def login(self, login: str, password: str):
        # result bool or session
        result = False
        # search User
        u = await User.select_where(
            cls_fields=[User.id, User.login, User.email, User.phone],
            conditions=[User.login == login, User.password == User.p_encrypt(password)]
        )
        # if isset
        if u:
            result = SessionManager().generate_session(data=dict(u[0]))
        return result

    # logout
    def logout(self, sid: str) -> bool:
        # delete
        SessionManager().del_session(sid)

        return True