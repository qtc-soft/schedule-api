from aiohttp.hdrs import METH_GET, METH_PUT, METH_POST, METH_DELETE
from controller import *


# list of a routes in application and it's handlers
routes = [
    (METH_GET,      '',                  ApiHelper),

    (METH_POST,     '/user-login',            UserAuthCommon),
    (METH_DELETE,   '/user-logout',           UserAuthCommon),
    (METH_GET,      '/user-confirm',          UserAuthCommon),
    # sid is access?
    (METH_POST,     '/is-auth',               IsAuth),

    (METH_POST,     '/customer-login',        CustomerAuthCommon),
    (METH_DELETE,   '/customer-logout',       CustomerAuthCommon),
    (METH_GET,      '/customer-confirm',      CustomerAuthCommon),

    (METH_GET,      '/users/{ids}',      User),
    (METH_POST,     '/user',             UserRegistration),
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

    (METH_GET,      '/orders/{ids}',      Order),
    (METH_POST,     '/orders',            Order),
    (METH_PUT,      '/orders',            Order),
    (METH_DELETE,   '/orders',            Order),

    # schedule data for customers
    (METH_GET,      '/customers/{ids}',      Customer),
    (METH_POST,     '/customers',            CustomerRegistration),
    (METH_PUT,      '/customers',            Customer),
    (METH_DELETE,   '/customers/{ids}',      Customer),

    (METH_GET,      '/schedule-online/{ids}',      ScheduleOnline),
]


# add all defined rout from variable `routes` into web application
def setup_routes(app):
    for route in routes:
        # setup base http routes
        app.router.add_route(route[0], route[1], route[2])

