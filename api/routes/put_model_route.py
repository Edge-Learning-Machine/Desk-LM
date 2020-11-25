import os
import numpy
import requests
import threading
import pandas as pd
from commons.error import *
from commons.status import *
from commons.checker import *
from commons.response import *
from commons.measurify import *

def put_model_route(request, database, id, app):
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

    # controllo parametri della richiesta
    try:
        check_schema(content, f'{os.getenv("SCHEMAS_PATH")}putSchema.json')
    except ValueError as error:
        return bad(error)

    # recupero il modello dal database
    try:
        doc = database.find_one(os.getenv('MODELS_COLLECTION'),{'_id':id})
    except ValueError as error:
        return bad(error)

    # verifico la modalità e avvio elm
    if content['mode'] == 'evaluate':
        # verifico che sia già stato inserito il dataset
        if not doc['dataset']:
            error = api_errors['invalid']
            error['details'] = 'Missing dataset'
            return bad(error)

        # aggiorno stato e database
        doc['status'] = Status.TRAINING.value
        if 'error' in doc: del doc['error']

        try:
            database.replace_one(os.getenv('MODELS_COLLECTION'), {'_id':doc['_id']}, doc)
        except ValueError as error:
            return bad(error)

        # avvio elm addestramento in parallelo (thread)
        from elm_manager import elm_manager
        elm_thread_evaluate = threading.Thread(
            target=elm_manager, 
            args=(app, content, database, doc, 'evaluate', ),
            kwargs={'webhook':doc['webhook'],})
        elm_thread_evaluate.start()

        return answer(doc)

    elif content['mode'] == 'predict':
        # verifico che sia gia stato addestrato
        if doc['status'] != Status.CONCLUDED.value:
            error = api_errors['invalid']
            error['details'] = 'Wait for the training'
            return bad(error)

        # aggiungo il model_id e rimuovo il mode dalla richiesta
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
            result = elm_manager(app, content, database, doc, 'predict')
            if isinstance(result, numpy.ndarray): 
                result = result.tolist()
            return answer({"predict": result})
        except ValueError as error:
            return bad(error)

    elif content['mode'] == 'measurify':
        # creo Dataset
        try:
            # recupero il token
            headers = { 'Authorization': postLogin() }

            # recupero gli items della feature
            res = getResource('features', content['feature'], {}, headers)

            columns = []
            for item in res['items']:
                if item['name'] in content['items']:
                    columns.append(item['name'])

            ds = {}
            for item in res['items']:
                ds[item['name']] = []

            params = {}
            params['filter'] = content['filter']
            params['page'] = 1

            while True:
                response = getResources('measurements', params, headers, True)
                for document in response['docs']:
                    for sample in document['samples']:
                        for i, v in enumerate(sample['values']):
                            ds[res['items'][i]['name']].append(v)
                if not response['nextPage']: break 
                params['page'] += 1

            dataset = pd.DataFrame(ds, columns=columns)

            # webhook
            if doc['webhook']:
                data = { 'progress': 50 }
                app.logger.info(f'Sending webhook ({doc["webhook"]["method"]}) to: {doc["webhook"]["url"]}')
                try:
                    requests.request(doc['webhook']['method'], doc['webhook']['url'], 
                            headers=headers, json=data, verify=False)
                except:
                    app.logger.error("Webhook not send")

        except Exception as e:
            error = api_errors['measurify']
            error['details'] = str(e)
            return bad(error)
    
        # avviare elm con dataset in parallelo (thread)
        from elm_manager import elm_manager
        elm_thread_measurify = threading.Thread(
            target=elm_manager, 
            args=(app, content, database, doc, 'measurify', ),
            kwargs={'dataset':dataset, 'columns':columns, 'target':content['target'], 'webhook':doc['webhook'], 'headers':headers})
        elm_thread_measurify.start()

        return answer(doc)