import asyncio
import random
import string
from settings import logger
import ujson
import time

from .session import Session


# TODO: Add object for configuration SessionManager
# TODO: connector should not be from other Managers

# meta-class
class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


# Singleton Session-manager
class SessionManager(metaclass=Singleton):
    __slots__ = '_pool', '_sids_users',

    def __init__(self):
        """ run self.set_session_type after init! """
        # all sessions, by user-id:sid
        self._pool = dict()
        # dict accordance sid:user_id
        self._sids_users = dict()

    # generate session by user_platform-type
    def generate_session(self, data: dict) -> Session:
        """ Generate new session by Entity-data. Return sid """
        # new session
        result = Session(data, sid=self.generate_sid())

        # save to pool
        self.add_session(result)
        logger.debug('Login: {}'.format(result))

        return result

    # add session to pool
    def add_session(self, session: Session):
        # save session: user-id:sid:dict
        self._pool.setdefault(session.id, {})
        self._pool[session.id][session.sid] = session

        # add accordance sid-user
        self._sids_users[session.sid] = session.id

    # isset session?
    def isset_session_by_sid(self, sid: str) -> bool:
        # return True if self._sids_users.get(sid) and self._pool[self._sids_users[sid]].get(sid) else False
        return True if self._sids_users.get(sid) else False

    # get session from loop by SID
    def get_session_by_sid(self, sid: str) -> Session:
        # Session or None
        return self._pool[self._sids_users[sid]][sid] if self.isset_session_by_sid(sid) else None

    # delete session & send empty message to mqtt for delete session
    def del_session(self, sid: str):
        # delete from pool & accordance sid-user
        if self.isset_session_by_sid(sid):
            self._pool[self._sids_users[sid]].pop(sid)
            self._sids_users.pop(sid)

        # log
        logger.debug('Logout: {}'.format(sid))

    # generate sid by session-type
    def generate_sid(self) -> str:
        """ generate new sid """
        return ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
