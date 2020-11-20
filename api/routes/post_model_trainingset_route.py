import os
from commons.error import *
from commons.status import *
from commons.checker import *
from commons.response import *

def post_model_trainingset_route(request, database, id):
    # verifico che l'utente sia autorizzato
    try: 
        check_authorization(database, request.headers.get('Authorization'))
    except:
        return bad(api_errors['auth'])

    # verifico che ci sia il file csv allegato
    file_csv = request.files.get('file')
    if not file_csv:
        error = api_errors['notfound']
        error['details'] = 'Missing csv file'
        return bad(error)

    # recupero il modello dal database
    try:
        doc = database.find_one(os.getenv('MODELS_COLLECTION'),{'_id':id})
    except ValueError as error:
        return bad(error)

    # modifico il modello con i dati per il dataset
    file_name = doc['_id']+'.csv'
    file_path = os.path.join(os.getenv('DATASETS_PATH'), file_name)
    doc['model']['ds'] = {}
    doc['model']['ds']['path'] = file_path
    for item in request.form:
        doc['model']['ds'][item] = json.loads(request.form[item])
    doc['status'] = Status.RUNNING.value
    doc['dataset'] = True
    if 'error' in doc: del doc['error']

    # controllo parametri del ds
    try:
        check_schema(doc["model"]['ds'], f'{os.getenv("SCHEMAS_PATH")}dsSchema.json')
    except ValueError as error:
        return bad(error)

    # salvo il file rinominandolo
    try:
        file_csv.save(file_path)
    except Exception as e:
        error = api_errors['generic']
        error['details'] = str(e)
        return bad(error)
    
    # aggiorno il database con il ds e il nuovo stato
    try:
        database.replace_one(os.getenv('MODELS_COLLECTION'), {'_id':id}, doc)
    except ValueError as e:
        return bad(error)

    return answer(doc)