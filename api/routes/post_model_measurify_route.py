import os
from commons.error import *
from commons.status import *
from commons.checker import *
from commons.response import *
from commons.measurify import *
import requests
import time

def post_model_measurify_route(request, database, id):
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

    # recupero il modello dal database
    try:
        value = database.find_one(os.getenv('MODELS_COLLECTION'),{'_id':id})
    except ValueError as error:
        return bad(error)

    # recupero il token
    headers = { 'Authorization': postLogin() }

    # recupero gli items della feature
    # res = getFeature(headers, content['feature'])
    res = getResource('features', content['feature'], {}, headers)

    # creo il file csv csv
    with open(f'datasets/{id}.csv', 'w') as file:
        first_row = []
        for item in res['items']:
            if item['name'] in content['items']:
                first_row.append(item['name'])
        file.write(','.join(first_row))

        params = {}
        params['filter'] = content['filter']
        params['page'] = 1

        while True:
            response = getResources('measurements', params, headers, True)
            for doc in response['docs']:
                for sample in doc['samples']:
                    row = []
                    for v in sample['values']:
                        row.append(str(v))
                    file.write('\n' + ','.join(row))
            if not response['nextPage']: 
                break 
            params['page'] += 1

    # modifico il modello con i dati per il dataset
    value['model']['ds'] = {}
    value['model']['ds']['path'] =  f'datasets/{id}.csv'
    value['model']['ds']['target_column'] = content['target']
    value['model']['ds']['select_columns'] = first_row

    # aggiorno lo stato 
    value['status'] = model_status[1]
    
    # aggiorno il database
    try:
        database.update_one(os.getenv('MODELS_COLLECTION'), {'_id':id}, {'$set':value})
    except ValueError as e:
        return bad(error)

    del value['model']

    return answer(value)