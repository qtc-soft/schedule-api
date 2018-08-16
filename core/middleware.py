"""
    Middleware
"""

from aiohttp import web, hdrs
from .exceptions import IncorrectParamsException, AccessException
from settings import logger
import asyncio


@web.middleware
# try-except middleware
async def filter_errors_request(request: web.Request, handler) -> web.Response:
    # allowed method OPTIONS
    if request.method == hdrs.METH_OPTIONS:
        return web.json_response(status=200)

    try:
        response = await handler(request)
    # exception "default params not validate", code = 400
    except IncorrectParamsException as e:
        logger.error(e)
        response = web.json_response(
            status=400,
            data=dict(
                errors=e.errors
            )
        )
    # exception "access denied"
    except AccessException as e:
        response = web.Response(status=e.code, reason=e.msg)
    # TODO: Write the correct handling of errors
    # other exceptions
    except Exception as e:
        if asyncio.get_event_loop().get_debug():
            raise e
        # else return response with code 500
        else:
            logger.error('Fail request, err: {}'.format(repr(e)))
            response = web.json_response(
                status=500,
                data={'errors': {
                    'reason': 'Error on running API-handlers: {}'.format(repr(e))
                }}
            )
    return response
