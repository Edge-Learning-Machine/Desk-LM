import os
import uuid
from commons.error import *
from commons.status import *
from commons.checker import *
from commons.response import *
from datetime import datetime

def post_model_route(request, database):
    # verifico che l'utente sia autorizzato
    try: 
        check_authorization(database, request.headers.get('Authorization'))
    except:
        return bad(api_errors['auth'])

    # verifico che la richiesta sia presente e in formato JSON valido
    try:
        content = check_json(request)
    except ValueError as error:
        return bad(error)

    # verifico parametri modello
    try:
        check_schema(content, f'{os.getenv("SCHEMAS_PATH")}postModelSchema.json')
    except ValueError as error:
        return bad(error)

    for param in content:
        try:
            check_schema(content[param], f'{os.getenv("SCHEMAS_PATH")}{param}Schema.json')
        except ValueError as error:
            return bad(error)

    # creazione nuovo modello
    new_model = {}
    new_model['model'] = content

    # aggiungo valori in risposta
    new_model['_id'] = str(uuid.uuid4())
    new_model['status'] = model_status[0]
    new_model['timestamp'] = str(datetime.now())

    if 'name' in content:
         # verifico che il name non sia giè stato usato
        if(database.exist(os.getenv('MODELS_COLLECTION'),{'name':content['name']})):
            error = api_errors['request']
            error['details'] = f'The name is already been used ({content["name"]})'
            return bad(error)
        # sposto 'name' fuori dal model
        new_model['name'] = new_model['model']['name']
        del new_model['model']['name']

    # inserisco nel database
    try:
        database.insert_one(os.getenv('MODELS_COLLECTION'), new_model)
    except ValueError as error:
        return bad(error)

    return answer(new_model)