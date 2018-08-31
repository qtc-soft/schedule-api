from aiohttp.hdrs import METH_GET, METH_PUT, METH_POST, METH_DELETE
from controller import *


# list of a routes in application and it's handlers
routes = [
    (METH_GET,      '',                  ApiHelper),
    (METH_POST,     '/login',            Login),
    (METH_POST,     '/logout',           Logout),
    (METH_POST,     '/registration',     Registration),

    (METH_GET,      '/users/{ids}',      User),
    # user can be created only from registration route
    # (METH_POST,     '/users',            User),
    (METH_PUT,      '/users',            User),
    (METH_DELETE,   '/users/{ids}',      User),

    (METH_GET,      '/schedules/{ids}',      Schedule),
    (METH_POST,     '/schedules',            Schedule),
    (METH_PUT,      '/schedules',            Schedule),
    (METH_DELETE,   '/schedules/{ids}',      Schedule),

    (METH_GET,      '/schedule-details/{ids}',      ScheduleDetail),
    (METH_POST,     '/schedule-details',            ScheduleDetail),
    (METH_PUT,      '/schedule-details',            ScheduleDetail),
    (METH_DELETE,   '/schedule-details/{ids}',      ScheduleDetail),

    (METH_GET,      '/customers/{ids}',      Customer),
    (METH_POST,     '/customers',            Customer),
    (METH_PUT,      '/customers',            Customer),
    (METH_DELETE,   '/customers/{ids}',      Customer),
]


# add all defined rout from variable `routes` into web application
def setup_routes(app):
    for route in routes:
        # setup base http routes
        app.router.add_route(route[0], route[1], route[2])

