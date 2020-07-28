import time
import markdown
import json
import jsonpickle
import markdown.extensions.fenced_code
import markdown.extensions.codehilite
import os
from pygments.formatters import HtmlFormatter
from flask import Flask, request, jsonify, send_file, Response
from pymongo import MongoClient
import uuid
from datetime import datetime
import threading
import sys

#global database, path, status, api_errors

base_token = 'src/BASE_TOKEN.json'
#BASE_TOKEN = 'BASE_TOKEN.json'

database = {
    "url": "mongodb://localhost:27017/",
    #"url": "mongodb://mongodb:27017/", 
    "name": "elm",
    "collections": [
        "clients",
        "models"
    ]
}

path = {
    "datasets": "datasets/",
    #"datasets": "/datasets/",
    "output": "out/",
    "zip": "zip/"
    #"zip": "/zip/"
}

status = [
    { 'code': 0, 'description': 'Model uploaded'},
    { 'code': 1, 'description': 'File csv uploaded'},
    { 'code': 2, 'description': 'Send to elm'},
    { 'code': 3, 'description': 'Training', 'perc': 0},
    { 'code': 4, 'description': 'Done'}
]

api_errors = {
    'no_token': 'Missing token',
    'no_db': 'Database not found',
    'unauth': 'Unauthorizated',
    'no_req': 'No request contents',
    'np_json': 'Request content not in JSON format',
    'no_json_valid': 'Request format not in valid JSON',
    'no_model': 'Model not found'
}

#creazone app flask
app = Flask(__name__)
port = int(os.environ.get('PORT', 5000))

#connessione al database
clientDB = MongoClient(database['url'])
cursor = clientDB[database['name']]
clients = cursor[database['collections'][0]]
models = cursor[database['collections'][1]]


def answer(content, status):
    if(status != 200):
        content = { 'error': content }
    return jsonify(content), status


@app.route('/model', methods=['POST'])
def set_model():
    #verifico che utente sia autorizzato
    if not request.headers.get('Authorization'):
        return answer(api_errors['no_token'], 400)

    try:
        client = clients.find_one({'token':request.headers['Authorization']})
    except:
        return answer(api_errors['no_db'], 404)

    if not client:
        return answer(api_errors['unauth'], 401)

    #verifico che la richiesta sia presente e in formato JSON valido
    if (not request.data):
        return answer(api_errors['no_req'], 400)
    if (not request.is_json):
        return answer(api_errors['no_json'], 400)
    try:
        jsonpickle.decode(request.data)
    except ValueError as e:
        return answer(api_errors['no_json_valid'] + ': ' + e, 400)
    content = request.get_json()

    # verifico che richiesta abbia tutti i campi necessari
    '''
    model_parameters = ['pp','est','ms','output']
    for parameter in model_parameters:
        if not parameter in content:
            return answer("Missing parameter: '" + parameter + "'", 400)
    '''
    #creazione nuovo modello
    new_model = {}
    new_model['model'] = content

    #aggiungo valori in risposta
    new_model['_id'] = str(uuid.uuid4())
    new_model['status'] = status[0]
    new_model['output'] = new_model['_id'] +'.zip'
    new_model['timestamp'] = str(datetime.now())

    #sposto webhook fuori dal model
    if 'webhook' in content:
        new_model['webhook'] = new_model['model']['webhook']
        del new_model['model']['webhook']

    #inserisco in mongodb
    try:
        models.insert_one(new_model)
    except:
        return answer(api_errors['no_db'], 404)

    return answer(new_model, 200)


@app.route('/model/<id>', methods=['GET'])
def get_model(id):
    #verifico che utente sia autorizzato
    if not request.headers.get('Authorization'):
        return answer(api_errors['no_token'], 400)

    try:
        client = clients.find_one({'token':request.headers['Authorization']})
    except:
        return answer(api_errors['no_db'], 404)

    if not client:
        return answer(api_errors['unauth'], 401)

    #recupero modello da mongo
    try:
        result = models.find_one({'_id':id})
    except:
        return answer(api_errors['no_db'], 404)

    if not result:
        return answer(api_errors['no_model'], 400)

    return answer(result, 200)


@app.route('/model/<id>/trainingset', methods=['POST'])
def upload_csv(id):
    #verifico che utente sia autorizzato    
    if not request.headers.get('Authorization'):
        return answer(api_errors['no_token'], 400)

    try:
        client = clients.find_one({'token':request.headers['Authorization']})
    except:
        return answer(api_errors['no_db'], 404)

    if not client:
        return answer(api_errors['unauth'], 401)

    #verifico che vi sia il file csv allegato
    if not request.files.get('file'):
        return answer("Missing csv file", 400)
    
    #verifico che vi siano i parametri necessari
    '''
    model_parameters = ['target_column','test_size']
    for parameter in model_parameters:
        if not parameter in request.form:
            return answer("Missing parameter: '" + parameter + "'", 400)
    '''

    #recupero da mongodb 
    try:
        result = models.find_one({'_id':id})
    except:
        return answer(api_errors['no_db'], 404)

    #se id non esiste
    if not result:
        return answer(api_errors['no_model'], 400)

    #Salva il file csv con il nuovo nome
    try:
        file_name = result['_id']+'.csv'
        f = request.files['file']
        file_path = os.path.join(path['datasets'], file_name)
        f.save(file_path)
    except:
        return answer("Error uploading file csv", 400)


    #aggiungo configurazione dataset
    result['model']['ds'] = {}
    result['model']['ds']['path'] = path['datasets'] + file_name
    
    for item in request.form:
        result['model']['ds'][item] = json.loads(request.form[item])
    
    '''   
    result['model']['ds']['path'] = path['datasets'] + file_name #
    result['model']['ds']['target_column'] = request.form['target_column']
    result['model']['ds']['test_size'] = float(request.form['test_size'])
    
    vector_parameters = ['skip_rows', 'skip_columns']
    for parameter in vector_parameters:
        if request.form.get(parameter):
            result['model']['ds'][parameter] = request.form.getlist(parameter)

    scalar_parameters = ['sep', 'decimal','categorical_multiclass']
    for parameter in scalar_parameters:
        if request.form.get(parameter):
            result['model']['ds'][parameter] = request.form.get(parameter)
    '''
    
    #aggiorno lo stato
    result['status'] = status[1]

    #aggiorno mongodb
    try:
        models.update_one({'_id':id}, {'$set':result})
    except:
        return answer(api_errors['no_db'], 404)

    return answer(result, 200)


@app.route('/model/<id>', methods=['PUT'])
def training(id):
    #verifico che utente sia autorizzato    
    if not request.headers.get('Authorization'):
        return answer(api_errors['no_token'], 400)

    try:
        client = clients.find_one({'token':request.headers['Authorization']})
    except:
        return answer(api_errors['no_db'], 404)

    if not client:
        return answer(api_errors['unauth'], 401)
    
    #verifico che la richiesta sia presente e in formato JSON valido
    if (not request.data):
        return answer(api_errors['no_req'], 400)
    if (not request.is_json):
        return answer(api_errors['no_json'], 400)
    try:
        jsonpickle.decode(request.data)
    except ValueError as e:
        return answer(api_errors['no_json_valid'] + ': ' + e, 400)

    content = request.get_json()

    #recupero modello da mongodb
    try:
        result = models.find_one({'_id':id})
    except:
        return answer(api_errors['no_db'], 404)

    #verifico che modello esista
    if not result:
        return answer(api_errors['no_model'], 400)

    #e che sia stato inserito il trainingset
    if result['status']['code'] < 1:
        return answer('You must first load the training set', 400)

    #verifico body
    if not content['evaluate']:
        return answer("Evaluate must be true to begin training", 400)

    #aggiorno stato e mongodb
    try:
        models.update_one({'_id':id}, {'$set':{'status':status[2]}})
        result = models.find_one({'_id':id})
    except:
        return answer(api_errors['no_db'], 404)

    # avvio thread per addestramento elm in parallelo
    import interface_elm
    thread = threading.Thread(target=interface_elm.int_elm, args=(id, app, models, result, path, status, api_errors, ))
    thread.start()

    return answer(result, 200)


@app.route('/model/<id>/<output>', methods=['GET'])
def download(id, output):
    #verifico che utente sia autorizzato    
    if not request.headers.get('Authorization'):
        return answer(api_errors['no_token'], 400)

    try:
        client = clients.find_one({'token':request.headers['Authorization']})
    except:
        return answer(api_errors['no_db'], 404)

    if not client:
        return answer(api_errors['unauth'], 401)

    #recupero modello da mongodb
    try:
        result = models.find_one({'_id':id})
    except:
        return answer(api_errors['no_db'], 404)

    #verifico che modello sia addestrato
    if result['status']['code'] != 4:
        return answer("Model not trained yet", 400)

    path_zip = '../' + path['zip'] + output
    #path_zip = path['zip'] + output

    return send_file(path_zip, as_attachment=True)


@app.errorhandler(404)
def notfound(error):
    return answer('Route not found', 404)


if __name__ == '__main__':
    try:
        results = clients.find({})
        if len(list(results)) == 0:
            print("API initialization")
            client = json.load(open(base_token))
            clients.insert_one(client)
    except:
        quit(api_errors['no_db'])

    app.run(debug=True, host='0.0.0.0', port=port, ssl_context='adhoc')