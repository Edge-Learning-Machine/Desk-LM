import os
from commons.error import *
from commons.status import *
from commons.checker import *
from commons.response import *
from flask import send_file

def get_model_download_route(request, database, id):
    # check authorization
    try: 
        check_authorization(database, request.headers.get('Authorization'))
    except:
        return bad(api_errors['auth'])

    # get model from the database
    try:
        doc = database.find_one(os.getenv('MODELS_COLLECTION'), {'_id':id})
    except ValueError as error:
        return bad(error)

    # check 'status' of the model
    if doc['status'] != Status.CONCLUDED.value:
        error = api_errors['invalid']
        error['details'] = 'Model not trainet yet'
        return bad(error)
    
    # check 'output' of the model
    if not doc['output']:
        error = api_errors['invalid']
        error['details'] = 'Model does not have an output configuration'
        return bad(error)
    
    path = f'{os.getenv("ZIP_PATH")}{doc["_id"]}.zip'

    # send zip dir
    if os.path.isfile(path):
        return send_file('../' + path, as_attachment=True)
    else:
        error = api_errors['notfound']
        error['details'] = 'zip file not found'
        return bad(error)