import os
from commons.error import *
from commons.status import *
from commons.checker import *
from commons.response import *
import requests
import urllib3
urllib3.disable_warnings()

def postLogin():
    url = f'{os.getenv("MEASURIFY_URL")}/login'
    body = {
        'username': os.getenv("MEASURIFY_USERNAME"),
        'password': os.getenv("MEASURIFY_PASSWORD")
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

def putResource(resource, id, headers, body):
    url = f'{os.getenv("MEASURIFY_URL")}/{resource}/{id}'
    response = requests.put(url, headers=headers, json=body, verify=False)
    return json.loads(response.content)