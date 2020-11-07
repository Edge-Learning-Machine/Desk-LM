import os
from commons.error import *
from commons.status import *
from commons.checker import *
from commons.response import *
from flask import send_file

def get_model_download_route(request, database, id):
    # verifico che l'utente sia autorizzato
    try: 
        check_authorization(database, request.headers.get('Authorization'))
    except:
        return bad(api_errors['auth'])

    # recupero il modello dal database
    try:
        doc = database.find_one(os.getenv('MODELS_COLLECTION'), {'_id':id})
    except ValueError as error:
        return bad(error)

    # verifico lo stato del modello
    if doc['status']['code'] < 4:
        error = api_errors['invalid']
        error['details'] = 'Model not trainet yet'
        return bad(error)
    
    path = f'{os.getenv("ZIP_PATH")}{doc["_id"]}.zip'

    if os.path.isfile(path):
        return send_file('../' + path, as_attachment=True)
    else:
        error = api_errors['notfound']
        error['details'] = 'zip file not found'
        return bad(error)