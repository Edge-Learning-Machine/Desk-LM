import os
from commons.error import *
from commons.status import *
from commons.checker import *
from commons.response import *
import requests

def postLogin(url):
    url = f'{url}/login'
    body = {
        'username': 'admin',
        'password': 'admin'
    }
    response = requests.post(url, json=body, verify=False)
    return json.loads(response.content)['token']

def getResources(url, resource, params, headers, stream=False):
    url = f'{url}/{resource}'
    response = requests.get(url, params=params, headers=headers, stream=stream, verify=False)
    return json.loads(response.content)

def getResource(url, resource, id, params, headers, stream=False):
    route = f'{resource}/{id}'
    return getResources(url, route, params, headers, stream)

def putResource(url, resource, id, headers, body):
    url = f'{url}/{resource}/{id}'
    response = requests.put(url, headers=headers, json=body, verify=False)
    return json.loads(response.content)