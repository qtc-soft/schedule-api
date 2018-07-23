import json
import asyncio
import uvloop
import random

from aiohttp import web, hdrs
from aiohttp_swagger import setup_swagger
from urllib.parse import urlparse

from common.managers.dbManager import DBManager
from settings import *
from core.middleware import filter_errors_request

from routes import setup_routes


# add headers for response
async def on_prepare(request, response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'X-AccessToken'
    response.headers['Access-Control-Allow-Methods'] = 'OPTIONS,GET,POST,PUT,DELETE'


# run service-api
def main(prefix_name: str='mgate'):
    # set uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    # get event-loop
    loop = asyncio.get_event_loop()

    # init settings
    init_settings()

    # create web application
    app = web.Application(
        middlewares=[filter_errors_request],
        loop=loop,
        debug=get_dev_mode(),
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
