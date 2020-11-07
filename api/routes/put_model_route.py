import os
import numpy
import threading
from commons.error import *
from commons.status import *
from commons.checker import *
from commons.response import *

def put_model_route(request, database, id, app):
    # verifico che l'utente sia autorizzato
    try: 
        check_authorization(database, request.headers.get('Authorization'))
    except:
        return bad(api_errors['auth'])

    # verifico che la richiesta sia presente e in formato JSON valido
    try:
        content = check_json(request)
    except Exception as error:
        return bad(error)

    # recupero il documento dal database
    try:
        doc = database.find_one(os.getenv('MODELS_COLLECTION'),{'_id':id})
    except ValueError as error:
        return bad(error)

    # verifico la modalità e avvio elm
    if 'mode' in content:
        if content['mode'] == 'evaluate':
            # verifico che sia già stato inserito il dataset
            if doc['status']['code'] < 1:
                error = api_errors['invalid']
                error['details'] = 'Missing csv file'
                return bad(error)

            # recupero id e parametri modello
            id = doc['_id']
            model = doc['model']

            # aggiorno stato e database
            doc['status'] = model_status[2]
            try:
                database.update_one(os.getenv('MODELS_COLLECTION'), {'_id':id}, {'$set':doc})
            except ValueError as error:
                return bad(error)

            # webhook
            webhook = None
            if 'webhook' in doc:
                webhook = doc['webhook']

            # avvio elm addestramento in parallelo (thread)
            from elm_manager import elm_manager
            elm_thread_evaluate = threading.Thread(target=elm_manager, args=('evaluate', database, id, model, app, content, webhook, ))
            elm_thread_evaluate.start()

            del doc['model']

            return answer(doc)

        elif content['mode'] == 'predict':
            # verifico che sia gia stato addestrato
            if doc['status']['code'] < 4:
                error = api_errors['invalid']
                error['details'] = 'Wait for the training'
                return bad(error)

            if not 'samples' in content:
                error = api_errors['request']
                error['details'] = "Missing 'samples' [] request"
                return bad(error)

            # aggiungo il model_id e rimuovo 'predict' dalla richiesta
            del content['mode']
            content['model_id'] = doc['_id']

            # controllo parametri del pr
            try: 
                check_schema(content, f'{os.getenv("SCHEMAS_PATH")}predictSchema.json')
            except ValueError as error:
                return bad(error)
                
            # avvio elm predizione
            from elm_manager import elm_manager
            try:
                result = elm_manager('predict', database, id, doc, app, content)
                if isinstance(result, numpy.ndarray): 
                    result = result.tolist()
                return answer({"predict": result})
            except ValueError as error:
                return bad(error)
        else:
            error = api_errors['request']
            error['details'] = "This mode is not allowed"
            return bad(error)
    else:
        error = api_errors['request']
        error['details'] = "Request must contain 'mode' param"
        return bad(error)