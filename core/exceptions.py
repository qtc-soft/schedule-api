"""
    Exceptions
"""


# Exception on incorrect default params in API
class IncorrectParamsException(Exception):
    def __init__(self, msg: str, errors: list=[]):
        super().__init__(msg)
        # list error by selector
        self.errors = errors or []

    # add error in errors
    def add_error(self, selector: str, reason: str, code: int=None):
        # default error
        item = dict(
            selector=selector,
            reason=reason
        )
        # add code
        if code:
            item['code'] = code
        # add in list errors
        self.errors.append(item)


# Exception on access denied
class AccessException(Exception):
    def __init__(self, msg: str = 'Access denied', code=403):
        super().__init__(msg)
        # code error for http
        self.msg = msg
        self.code = code