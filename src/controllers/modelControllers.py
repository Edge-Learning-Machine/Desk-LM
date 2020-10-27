import os
import uuid
import json
import threading
from commons.error import *
from commons.status import *
from commons.checker import *
from commons.response import *
from datetime import datetime
from flask import send_file

def get_models_route(request, database):
    # verifico che utente sia autorizzato
    error, code = check_authorization(request, database)
    if error:
        return answer(error, code)

    # recupero i modelli dal database
    error, values = database.find(os.getenv('MODELS_COLLECTION'),'')
    if error:
        return answer(error, 404)

    result = {}
    i = 1
    for value in values:
        result[i] = value['_id']
        i += 1

    return answer(result, 200)


def get_model_route(request, database, id):
    # verifico che utente sia autorizzato
    error, code = check_authorization(request, database)
    if error:
        return answer(error, code)
    
    # recupero il modello dal database
    error, value = database.find_one(os.getenv('MODELS_COLLECTION'),{'_id':id})
    if error:
        return answer(error, 404)

    if not value:
        return answer(api_errors['no_model'], 400)

    return answer(value, 200)


def post_model_route(request, database):
    # verifico che utente sia autorizzato
    error, code = check_authorization(request, database)
    if error:
        return answer(error, code)

    # verifico che la richiesta sia presente e in formato JSON valido
    error, code, content = check_json(request)
    if error:
        return answer(error, code)

    # verifico parametri modello
    error, code = check_schema(content, 'jsonSchema/api_model_schema.json')
    if error:
        message = api_errors['no_params'] + ' - ' + 'api model'
        return answer(message, code)

    for param in content:
        error, code = check_schema(content[param], 'jsonSchema/'+param+'Schema.json')
        if error:
            message = api_errors['no_params'] + ' - ' + param
            return answer(message, code)

    # creazione nuovo modello
    new_model = {}
    new_model['model'] = content

    # aggiungo valori in risposta
    new_model['_id'] = str(uuid.uuid4())
    new_model['status'] = model_status[0]
    new_model['output'] = os.getenv('ZIP_PATH') + new_model['_id'] +'.zip'
    new_model['timestamp'] = str(datetime.now())

    # sposto webhook fuori dal model
    if 'webhook' in content:
        new_model['webhook'] = new_model['model']['webhook']
        del new_model['model']['webhook']

    # inserisco nel database
    error = database.insert_one(os.getenv('MODELS_COLLECTION'), new_model)
    if error:
        return answer(error, 404)

    return answer(new_model, 200)


def post_model_trainingset_route(request, database, id):
    # verifico che utente sia autorizzato
    error, code = check_authorization(request, database)
    if error:
        return answer(error, code)

    # verifico che ci sia il file csv allegato
    file_csv = request.files.get('file')
    if not file_csv:
        return answer(api_errors['no_csv'], 400)

    # recupero il modello dal database 
    error, value = database.find_one(os.getenv('MODELS_COLLECTION'),{'_id':id})
    if error:
        return answer(error, 404)

    # verifico che il modello esista
    if not value:
        return answer(api_errors['no_model'], 400)

    # modifico il modello con i dati per il dataset
    file_name = value['_id']+'.csv'
    file_path = os.path.join(os.getenv('DATASETS_PATH'), file_name)
    value['model']['ds'] = {}
    value['model']['ds']['path'] = file_path
    for item in request.form:
        value['model']['ds'][item] = json.loads(request.form[item])

    # controllo parametri del ds
    error, code = check_schema(value["model"]['ds'], 'jsonSchema/dsSchema.json')
    if error:
        message = api_errors['no_params'] + ' - ' + 'ds'
        return answer(message, code)

    # salvo il file rinominandolo
    try:
        file_csv.save(file_path)
    except:
        return answer(api_errors['no_save'], 400)

    # aggiorno lo stato 
    value['status'] = model_status[1]
    
    # aggiorno il database
    error = database.update_one(os.getenv('MODELS_COLLECTION'), {'_id':id}, {'$set':value})
    if error:
        return answer(error, 404)

    return answer(value, 200)


def put_model_route(request, database, id, app):
    # verifico che utente sia autorizzato
    error, code = check_authorization(request, database)
    if error:
        return answer(error, code)

    # verifico che la richiesta sia presente e in formato JSON valido
    error, code, content = check_json(request)
    if error:
        return answer(error, code)

    # recupero il modello dal database
    error, value = database.find_one(os.getenv('MODELS_COLLECTION'), {'_id':id})
    if error:
        return answer(error, 404)

    # verifico che il modello esista
    if not value:
        return answer(api_errors['no_model'], 400)

    # verifico che sia già stato inserito il dataset
    if value['status']['code'] < 1:
        return answer(api_errors['no_csv'], 400)

    # avvio elm addestramento
    if 'evaluate' in content and content['evaluate']:
        # aggiorno stato e database
        value['status'] = model_status[2]
        error = database.update_one(os.getenv('MODELS_COLLECTION'), {'_id':id}, {'$set':value})
        if error:
            return answer(error, 404)

        # avvio elm addestramento in parallelo (thread)
        from elm_manager import elm_manager
        elm_thread_evaluate = threading.Thread(target=elm_manager, args=('evaluate', database, id, value, app, content, ))
        elm_thread_evaluate.start()

        return answer(value, 200)

    # avvio elm predizione
    elif 'predict' in content and content['predict']:
        # verifico che sia gia stato addestrato
        if value['status']['code'] < 4:
            return answer("Wait for the training", 400)
        if not 'samples' in content:
           return answer("Missing samples", 400)
            
        # avvio elm predizione
        from elm_manager import elm_manager
        result = elm_manager('predict', database, id, value, app, content)

        return answer({"predict": result.tolist()}, 200)
    else:
        return answer("Bad request", 400)


def get_model_download_route(request, database, id):
    # verifico che utente sia autorizzato
    error, code = check_authorization(request, database)
    if error:
        return answer(error, code)

    # recupero il modello dal database
    error, value = database.find_one(os.getenv('MODELS_COLLECTION'), {'_id':id})
    if error:
        return answer(error, 404)

    # verifico che il modello esista
    if not value:
        return answer(api_errors['no_model'], 400)

    # verifico lo stato del modello
    if value['status']['code'] < 4:
        return answer(api_errors['no_train'], 400)

    return send_file('../' + value['output'], as_attachment=True)


def delete_model_route(request, database, id):
    # verifico che utente sia autorizzato
    error, code = check_authorization(request, database)
    if error:
        return answer(error, code)

    # recupero il modello dal database
    error, value = database.find_one(os.getenv('MODELS_COLLECTION'), {'_id':id})
    if error:
        return answer(error, 404)

    # verifico che il modello esista
    if not value:
        return answer(api_errors['no_model'], 400)

    # elimino il file csv (se esiste)
    if value['status']['code'] > 0:
        if os.path.isfile(value['model']['ds']['path']):
            os.remove(value['model']['ds']['path'])

    # elimino lo zip (se esiste)
    if 'output' in value:
        if os.path.isfile(value['output']):
            os.remove(value['output'])

    # elimino lo storage (se esiste)
    if 'storage' in value:
        if os.path.isfile('storage/' + value['storage'] + '.pkl'):
            os.remove('storage/' + value['storage'] + '.pkl')

    # elimino il documento dal database
    error = database.delete_one(os.getenv('MODELS_COLLECTION'), {'_id':id})
    if error:
        return answer(error, 404)

    return answer({'succes':'Model deleted!'}, 200)