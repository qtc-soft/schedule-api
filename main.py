import json
import asyncio
import uvloop
import random

from aiohttp import web, hdrs
from aiohttp_swagger import setup_swagger
from urllib.parse import urlparse
import jinja2
import aiohttp_jinja2

from common.managers.dbManager import DBManager
from settings import *
from core.middleware import filter_errors_request

from routes import setup_routes

from common.managers.sessionManager import SessionManager

# add headers for response
async def on_prepare(request, response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'X-AccessToken'
    response.headers['Access-Control-Allow-Methods'] = 'OPTIONS,GET,POST,PUT,DELETE'


# run service-api
def main(prefix_name: str='schedule-online', is_debug=False):
    # set uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    # get event-loop
    loop = asyncio.get_event_loop()

    # init settings
    init_settings()
    logger.info('{}:debug is {}'.format(prefix_name, is_debug))
    # set debug (or not) to loop
    loop.set_debug(is_debug)

    # create web application (with set debug)
    app = web.Application(
        middlewares=[filter_errors_request],
        loop=loop,
        debug=is_debug,
        client_max_size=1024 ** 2 * 64
    )

    # add Headers for request
    app.on_response_prepare.append(on_prepare)

    # set settings for DBManager
    DBManager().set_settings(dict(
        user=config.get('DB', 'user'),
        password=config.get('DB', 'password'),
        database=config.get('DB', 'database'),
        host=config.get('DB', 'host'),
        port=config.get('DB', 'port')
    ))
    # initial connection-poll in DBManager
    loop.run_until_complete(loop.create_task(DBManager().init_pool()))
    app.on_shutdown.append(DBManager().on_shutdown)

    # add jinja2-templates
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('templates'))

    # add link to session in web.app
    app.session_storage = SessionManager()
    # auth header name
    app.auth_header_name = config.get('SERVICE', 'auth_header_name')

    # add routes
    setup_routes(app)

    # get url for run web-app
    bind_url = urlparse(config.get('PUBLIC_API', 'bind'))

    # run swagger
    setup_swagger(app,
                  swagger_url='/api/docs',
                  title='Schedule online docs',
                  description='',
                  api_version='0.1',
                  contact='schedule_online@gmail.com')

    # run web application
    try:
        web.run_app(
            app,
            host=bind_url.hostname,
            port=bind_url.port,
            reuse_address=True,
            reuse_port=True,
            shutdown_timeout=1
        )
    finally:
        loop.close()


# run service regardless
if __name__ == "__main__":
    main()
