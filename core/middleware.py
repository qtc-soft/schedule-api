"""
    Middleware
"""

from aiohttp import web, hdrs
from core.exceptions import IncorrectParamsException
from settings import logger


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
    # TODO: Write the correct handling of errors
    except Exception as e:
        # if dev - exception
        raise e
        # TODO: enable code by after fix DEV_MOD
        # if DEV_MOD:
        #     raise e
        # # else return response with code 500
        # else:
        #     logger.error('Fail request, err: ', e)
        #     response = web.json_response(
        #         status=500,
        #         data={'errors': {
        #             'reason': 'Error on running API-handlers: %s' % e
        #         }}
        #     )
    return response
