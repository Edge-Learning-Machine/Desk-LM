import os
import uuid
from commons.error import *
from commons.status import *
from commons.checker import *
from commons.response import *
from datetime import datetime

def post_model_route(request, database):
    # check authorization
    try: 
        check_authorization(database, request.headers.get('Authorization'))
    except:
        return bad(api_errors['auth'])

    # check json format
    try:
        content = check_json(request)
    except ValueError as error:
        return bad(error)

    # check model params
    try:
        check_schema(content, f'{os.getenv("SCHEMAS_PATH")}postModelSchema.json')
    except ValueError as error:
        return bad(error)

    for param in content:
        try:
            check_schema(content[param], f'{os.getenv("SCHEMAS_PATH")}{param}Schema.json')
        except ValueError as error:
            return bad(error)

    # new model creation
    new_model = {}
    new_model['model'] = content

    # aggiungo valori in risposta
    new_model['_id'] = str(uuid.uuid4())
    new_model['status'] = Status.RUNNING.value
    new_model['dataset'] = False
    new_model['timestamp'] = str(datetime.now())

    # output
    if 'output' in content:
        new_model['output'] = f"{new_model['_id']}.zip"
    else:
        new_model['output'] = None

    # webhook
    if 'webhook' in content:
        new_model['webhook'] = content['webhook']
        del new_model['model']['webhook']
    else:
        new_model['webhook'] = None

    # add to database
    try:
        database.insert_one(os.getenv('MODELS_COLLECTION'), new_model)
    except ValueError as error:
        return bad(error)

    return answer(new_model)