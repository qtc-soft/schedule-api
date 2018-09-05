from aiohttp.hdrs import METH_GET, METH_PUT, METH_POST, METH_DELETE
from controller import *


# list of a routes in application and it's handlers
routes = [
    (METH_GET,      '',                  ApiHelper),

    (METH_POST,     '/user-login',            UserLogin),
    (METH_POST,     '/user-logout',           UserLogout),
    (METH_POST,     '/user-registration',     UserRegistration),

    (METH_POST,     '/custom-login',            CustomLogin),
    (METH_POST,     '/custom-logout',           CustomLogout),
    (METH_POST,     '/custom-registration',     CustomRegistration),

    (METH_GET,      '/users/{ids}',      User),
    (METH_PUT,      '/users',            User),
    (METH_DELETE,   '/users/{ids}',      User),

    (METH_GET,      '/schedules/{ids}',      Schedule),
    (METH_POST,     '/schedules',            Schedule),
    (METH_PUT,      '/schedules',            Schedule),
    (METH_DELETE,   '/schedules/{ids}',      Schedule),

    # schedule data for customers
    (METH_GET,      '/schedule-online/{ids}',      ScheduleOnline),

    (METH_GET,      '/schedule-details/{ids}',      ScheduleDetail),
    (METH_POST,     '/schedule-details',            ScheduleDetail),
    (METH_PUT,      '/schedule-details',            ScheduleDetail),
    (METH_DELETE,   '/schedule-details/{ids}',      ScheduleDetail),

    (METH_GET,      '/orders/{ids}',      Order),
    (METH_POST,     '/orders',            Order), # only for customers
    (METH_PUT,      '/orders',            Order), # only for customers

    (METH_GET,      '/customers/{ids}',      Customer), # only for users
    (METH_POST,     '/customers',            Customer), # only for customers
    (METH_PUT,      '/customers',            Customer),
]


# add all defined rout from variable `routes` into web application
def setup_routes(app):
    for route in routes:
        # setup base http routes
        app.router.add_route(route[0], route[1], route[2])

