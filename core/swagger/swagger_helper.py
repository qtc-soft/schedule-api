from os.path import abspath, dirname, join
import types
import yaml
from jinja2 import Template
from aiohttp.web import StaticResource, DynamicResource
from aiohttp.hdrs import METH_GET, METH_PUT, METH_POST, METH_DELETE

from core.web_view import ExtendedApiView

try:
    import ujson as json
except ImportError:
    import json


SWAGGER_TEMPLATE = abspath(join(dirname(__file__), "templates"))


# TODO: Add text (decr/titles/other) from function-docs
# generate json-data for swagger
def generate_swagger_info(app,
                          auth_header_name: str,
                          api_base_url: str = "/",
                          description: str = "Swagger API definition",
                          api_version: str = "1.0.0",
                          title: str = "Swagger API",
                          contact: str = "", *args, **kwargs):

    # Load base Swagger template
    with open(join(SWAGGER_TEMPLATE, "swagger.yaml"), "r") as f:
        swagger_base = (
            Template(f.read()).render(
                description=description,
                version=api_version,
                title=title,
                contact=contact,
                base_path=api_base_url)
        )

    # The Swagger OBJ
    swagger = yaml.load(swagger_base)
    swagger["paths"] = {}

    # if isset access-token - add header
    if auth_header_name:
        swagger['securityDefinitions'] = {
            auth_header_name: {
                'type': 'apiKey',
                'name': auth_header_name,
                'in': 'header'
            }
        }

    # definitions for swagger
    definitions = {}
    # by routes
    for route in app.router.routes():
        # print(route.method, route.get_info(), type(route.resource))
        if not type(route.resource) == StaticResource and \
                not isinstance(route.handler, types.FunctionType) and \
                not isinstance(route.handler, types.MethodType) and \
                issubclass(route.handler, ExtendedApiView):
            # handler-class
            handler_cls = route.handler
            # method of request
            request_method = route.method.lower().upper()
            # route-info
            route_info = route.get_info()
            # route-path
            route_path = route_info.get('path') or route_info.get('formatter')

            end_point_doc_by_method = {
                'tags': [handler_cls.__name__],
                # 'summary': '111111',
                # 'description': '222222222',
                'producer': 'application/json',
                'parameters': [],
                # 'responses': {
                #     '200': {
                #         'description': 'successful operation'
                #     }
                # }
            }

            # schema for get-params
            schema = handler_cls._get_params_schemas().get(request_method)
            # calc get-params
            if schema:
                for param_field in schema.fields.values():
                    # calc type get-param
                    if '{%s}' % param_field.name in route_path:
                        param_in = 'path'
                    else:
                        param_in = 'query'
                    # TODO: cal param 'type' (string/integer) from schema
                    end_point_doc_by_method['parameters'].append({
                        'in': param_in,
                        'name': param_field.name,
                        # 'description': param_field.name,
                        'required': param_field.required,
                        'default': param_field.default if param_field.default else '',
                        'type': 'string'
                    })

            # add body-aprams
            if request_method in {METH_POST, METH_PUT}:
                try:
                    # model whith logic-code
                    logic_model_class = handler_cls.get_model.__annotations__.get('return')
                except:
                    pass
                else:
                    if logic_model_class:
                        # schema-validate
                        schema = logic_model_class._get_create_schema() if request_method == METH_POST else logic_model_class._get_update_schema()
                        # calc body-params
                        param_items = {}
                        # TODO: cal param 'type' (string/integer) from schema
                        for param_field in schema.fields.values():
                            if not param_field.dump_only:
                                param_items[param_field.name] = {
                                    # 'description': param_field.name,
                                    'required': param_field.required,
                                    'default': param_field.default if param_field.default else '',
                                    'type': 'string'
                                }

                        definition_name = '{}/{}'.format(logic_model_class.__name__, request_method)
                        # add definition
                        definitions[definition_name] = {
                            'type': 'object',
                            'properties': param_items
                        }
                        # add body-params
                        end_point_doc_by_method['parameters'].append({
                            'in': 'body',
                            'name': 'item-value',
                            'required': 'true',
                            'schema': {
                                'type': 'array',
                                'items': {
                                    '$ref': '#/definitions/{}'.format(definition_name),
                                }
                            }
                        })

            # add to docs
            swagger['paths'].setdefault(route_path, {})
            swagger['paths'][route_path][request_method.lower()] = end_point_doc_by_method
            # set definitions
            swagger['definitions'] = definitions

    return swagger
