import os
from commons.error import *
from commons.status import *
from commons.checker import *
from commons.response import *


def delete_model_route(request, database, id):
    # verifico che l'utente sia autorizzato
    try: 
        check_authorization(database, request.headers.get('Authorization'))
    except:
        return bad(api_errors['auth'])

    # recupero il modello dal database
    try:
        value = database.find_one(os.getenv('MODELS_COLLECTION'),{'_id':id})
    except ValueError as error:
        return bad(error)

    # elimino il file csv (se esiste)
    if 'ds' in value['model']:
        if os.path.isfile(value['model']['ds']['path']):
            os.remove(value['model']['ds']['path'])

    # elimino lo zip (se esiste)
    zipfile = f'{os.getenv("ZIP_PATH")}{value["_id"]}.zip'
    if os.path.isfile(zipfile):
        os.remove(zipfile)

    # elimino lo storage (se esiste)
    storagefile = f'{os.getenv("STORAGE_PATH")}{value["_id"]}.pkl'
    if os.path.isfile(storagefile):
        os.remove(storagefile)

    # elimino il documento dal database
    try:
        database.delete_one(os.getenv('MODELS_COLLECTION'), {'_id':id})
    except ValueError as e:
        return bad(error)

    return answer({'succes':f'Model [{id}] deleted!'})