import os
from commons.error import *
from commons.status import *
from commons.checker import *
from commons.response import *
import requests

def postLogin():
    url = f'{os.getenv("MEASURIFY_URL")}/login'
    body = {
        'username': 'admin',
        'password': 'admin'
    }
    response = requests.post(url, json=body, verify=False)
    return json.loads(response.content)['token']

def getResources(resource, params, headers, stream=False):
    url = f'{os.getenv("MEASURIFY_URL")}/{resource}'
    response = requests.get(url, params=params, headers=headers, stream=stream, verify=False)
    return json.loads(response.content)

def getResource(resource, id, params, headers, stream=False):
    route = f'{resource}/{id}'
    return getResources(route, params, headers, stream)