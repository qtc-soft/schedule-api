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
