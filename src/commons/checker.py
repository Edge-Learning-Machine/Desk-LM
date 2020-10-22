from config import *
from flask import jsonify
import json
import jsonpickle
import os

def answer(content, status):
    if(status != 200):
        content = { 'error': content }
    return jsonify(content), status


# Return (error, code)
def check_authorization(request, database):
    error, code, value = database.find_one(os.getenv('CLIENTS_COLLECTION'),{'token':request.headers.get('Authorization')})
    if error:
        return (value, 404)
    if not value:
        return (api_errors['no_auth'], 401)
    return (None, None)

# Return (error, code, content)
def check_json(request):
    if(not request.data):
        return (api_errors['no_req'], 400, None)
    if(not request.is_json):
        return (api_errors['no_json'], 400, None)
    try:
        value = jsonpickle.decode(request.data)
    except ValueError as e:
        return (api_errors['no_json_valid'] + ': ' + str(e), 400, None)
    return (None, None, value)
