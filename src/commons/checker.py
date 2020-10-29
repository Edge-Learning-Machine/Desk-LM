import os
import json
import jsonpickle
from commons.error import *
from jsonschema import validate


def check_authorization(request, database):
    """
    Returns:
        string: error
        int: code
    """
    error, value = database.find_one(os.getenv('CLIENTS_COLLECTION'),{'token':request.headers.get('Authorization')})
    if error:
        return error, 404
    if not value:
        return api_errors['no_auth'], 401
    return None, None


def check_json(request):
    """
    Returns:
        string: error
        int: code
        object: value
    """
    if(not request.data):
        return (api_errors['no_req'], 400, None)
    if(not request.is_json):
        return (api_errors['no_json'], 400, None)
    try:
        value = jsonpickle.decode(request.data)
    except ValueError as e:
        return (api_errors['no_json_valid'] + ': ' + str(e), 400, None)
    return (None, None, value)


def check_schema(model, file_schema):
    """
    Returns:
        string: error
        int: code
    """
    schema = json.load(open(file_schema))
    try:
        validate(instance=model, schema=schema)
    except Exception as e:
        return (e, 400)
    return (None, None)
