import os
from commons.error import *
from commons.checker import *
from commons.response import *

def get_models_route(request, database):
    # verifico che l'utente sia autorizzato
    try: 
        check_authorization(database, request.headers.get('Authorization'))
    except:
        return bad(api_errors['auth'])

    # recupero i modelli dal database
    try:
        docs = database.find(os.getenv('MODELS_COLLECTION'),'')
    except ValueError as error:
        return bad(error)

    result = []
    for doc in docs:
        try:
            value = database.find_one(os.getenv('MODELS_COLLECTION'), {'_id':str(doc['_id'])})
        except ValueError as error:
            return bad(error)
        del value['model']
        result.append(value)

    return answer(result)