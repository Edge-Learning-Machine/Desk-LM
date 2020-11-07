import os
import json
import jsonpickle
import jsonschema
from commons.error import *
from jsonschema import validate


def check_authorization(database, token):
    try:
        value = database.find_one(os.getenv('CLIENTS_COLLECTION'),{'token':token})
    except ValueError as error:
        raise error

def check_json(request):
    if(not request.data):
        error = api_errors['request']
        error['details'] = 'No request content'
        raise ValueError(error)
    if(not request.is_json):
        error = api_errors['request']
        error['details'] = 'Request content not in JSON format'
        raise ValueError(error)
    try:
        value = jsonpickle.decode(request.data)
    except ValueError as e:
        error = api_errors['request']
        error['details'] = 'Request format not in valid JSON'
        raise ValueError(error)
    return value


def check_schema(model, file_schema):
    try:
        with open(file_schema) as schema:
            schema = json.load(schema)
    except FileNotFoundError as e:
        error = api_errors['notfound']
        error['details'] = f'{e.filename} - {e.strerror}'
        raise ValueError(error)
    try:
        validate(instance=model, schema=schema)
    except jsonschema.exceptions.ValidationError as e:
        error = api_errors['validation']
        error['details'] = f'{e.message}'
        raise ValueError(error)
    except ValueError as e:
        error = api_errors['generic']
        raise ValueError(error)