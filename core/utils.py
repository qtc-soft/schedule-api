import string
import random

import asyncio
from aiohttp import web


# enable aiohtt-debugtoolbar for Application, route: /_debugtoolbar
def enable_debugtoolbar(app: web.Application):
    import aiohttp_debugtoolbar
    from aiohttp_debugtoolbar import toolbar_middleware_factory
    app.middlewares.append(toolbar_middleware_factory)
    aiohttp_debugtoolbar.setup(app)


# func-callback by finished Task
def task_finished_callback(task: asyncio.Task, res: list, err: list):
    # get task-result
    task_result = task.result()
    # if result
    if task_result:
        if task_result[0]:
            if isinstance(task_result[0], list):
                res.extend(task_result[0])
            else:
                res.append(task_result[0])
        # if errors
        if task_result[1]:
            if isinstance(task_result[1], list):
                err.extend(task_result[1])
            else:
                err.append(task_result[1])
    else:
        err.append(get_error_item(reason='Undefined error'))


# calc errors from validate-data (errors) by UnmarshalResult
def calc_errors_from_vd(errors: dict, data_on_validate: dict={}) -> list:
    # result list errors
    result_errors = []
    # errors = {field_name: [errors-msgs]}
    for field_name in errors:
        for msg in errors[field_name]:
            result_errors.append(get_error_item(selector=field_name, value=data_on_validate.get(field_name) if type(data_on_validate) == dict else data_on_validate, reason=msg))
    return result_errors


# standard error item
def get_error_item(selector: str='', value=None, reason: str='Not found', **kwargs) -> dict:
    """
    :param selector: str. Selector/field of error
    :param reason: str. Reason of error
    :param value: value. Value/id/selector-value
    :param kwargs: other params - added ro dict error
    :return: dict. Item error
    """
    # default dict
    error = dict(
        reason=reason
    )
    if selector:
        error['selector'] = selector
    # add value
    if value:
        error['value'] = value
    # add other fields
    if kwargs:
        for i in kwargs:
            error[i] = kwargs[i]
    return error


# standard result item
def get_result_item(data, fields) -> dict:
    """
    :param data: dict or asyncpgsa.record.Record
    :param fields: list or set
    :return: dict
    """
    result = {}
    # if dict
    if isinstance(data, dict):
        for field in fields:
            result[field] = data.get(field, None)
    # if Record
    else:
        for field in fields:
            try:
                result[field] = data[field]
            except:
                result[field] = None
    return result


# validate dict by schema
def validate_by_schema(schema, data: dict) -> {dict, list}:
    # validate-data
    v_data, errors = None, []
    # validate
    vd = schema.load(data)
    # if error return error-item
    if vd.errors:
        errors.extend(calc_errors_from_vd(errors=vd.errors, data_on_validate=data))
    else:
        v_data = vd.data
    return v_data, errors


# generate unique key
def keygen (size=12, chars=string.ascii_uppercase + string.digits) -> str:
    """
    :param size:
    :param chars:
    :return: String with unique key
    """
    return ''.join(random.choice(chars) for _ in range(size))