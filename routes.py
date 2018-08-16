from aiohttp.hdrs import METH_GET, METH_PUT, METH_POST, METH_DELETE
from controller import ApiHelper
from controller import User
from controller import Login
from controller import Logout


# list of a routes in application and it's handlers
routes = [
    (METH_GET,      '',                  ApiHelper),
    (METH_POST,     '/login',            Login),
    (METH_POST,     '/logout',           Logout),

    (METH_GET,      '/users/{ids}',      User),
    (METH_POST,     '/users',            User),
    (METH_PUT,      '/users',            User),
    (METH_DELETE,   '/users/{ids}',      User)
]


# add all defined rout from variable `routes` into web application
def setup_routes(app):
    for route in routes:
        # setup base http routes
        app.router.add_route(route[0], route[1], route[2])

