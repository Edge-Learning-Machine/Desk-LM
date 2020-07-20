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


data = {
    "database": "elm",
    "collection": "models"
}

app = Flask(__name__)
port = int(os.environ.get('PORT', 5000))

client = MongoClient("mongodb://localhost:27017/")
cursor = client[data['database']]
collection = cursor[data['collection']]


def answer(content, status):
    if(status != 200):
        content = { 'error': content }
    return jsonify(content), status



@app.route('/model', methods=['POST'])
def set_model():
    if (not request.data):
        return answer('No request contents', 400)
    if (not request.is_json):
        return answer('Request content not in JSON format', 400)
    try:
        jsonpickle.decode(request.data)
    except ValueError as e:
        return answer('Request format not in valid JSON: ' + e, 400)

    content = request.get_json()

    # verifico che richiesta abbia tutti i campi necessari
    model_parameters = ['e','p','s','o','webhook']
    for parameter in model_parameters:
        if not parameter in content:
            return answer("Missing parameter: '" + parameter + "'", 400)
    #...

    #aggiungo valori in risposta
    content['_id'] = str(uuid.uuid4())
    content['status'] = '0: Model uploaded'
    content['output'] = 'zip/'+ content['_id'] +'.zip'
    content['timestamp'] = str(datetime.now())
    #...

    #inserisco nella collezione
    try:
        collection.insert_one(content)
    except:
        return answer('Database not connected', 400)
    #...

    return answer(content, 200)


@app.route('/model/<id>', methods=['GET'])
def get_model(id):
    try:
        result = collection.find_one({'_id':id})
    except:
        return answer('Database not connected', 400)

    if not result:
        return answer('Model not existing', 400)

    return answer(result, 200)


@app.route('/model/<id>/trainingset', methods=['POST'])
def upload_csv(id):    
    if not request.files.get('file'):
        return answer("Missing .csv file", 400)
    
    if not request.form.get('target_column'):
        return answer("Missing target_column parameter", 400)

    try:
        result = collection.find_one({'_id':id})
    except:
        return answer('Database not connected', 400)

    if not result:
        return answer("Model not existing", 400)

    #Salva il file csv con il nuovo nome
    try:
        name_csv = str(uuid.uuid4())+'.csv'
        f = request.files['file']
        f.save('datasets/'+ name_csv)
    except:
        return answer("Error uploading the file", 400)
    #...

    result['d'] = {}
    result['d']['path'] = 'datasets/' + name_csv
    result['d']['target_column'] = request.form['target_column']
    
    vector_parameter = ['skip_rows', 'skip_columns']
    for parameter in vector_parameter:
        if request.form.get(parameter):
            result['d'][parameter] = request.form.getlist(parameter)

    vector_parameter = ['sep', 'decimal','test_size','categorical_multiclass']
    for parameter in vector_parameter:
        if request.form.get(parameter):
            result['d'][parameter] = request.form.get(parameter)
    
    result['status'] = '1: CSV uploaded'

    try:
        collection.update_one({'_id':id}, {'$set':result})
    except:
        return answer("Database not connected", 400)

    return answer(result, 200)


@app.route('/model/<id>', methods=['PUT'])
def training(id):
    if (not request.data):
        return answer('No request contents', 400)
    if (not request.is_json):
        return answer('Request content not in JSON format', 400)
    try:
        jsonpickle.decode(request.data)
    except ValueError as e:
        return answer('Request format not in valid JSON: ' + e, 400)

    try:
        result = collection.find_one({'_id':id})
    except:
        return answer('Database not connected', 400)

    if not result:
        return answer("Model not existing", 400)

    content = request.get_json()

    if not content['evaluate']:
        return answer("Evaluate must be true to begin training", 400)

    try:
        result = collection.update_one({'_id':id}, {'$set':{'status':'2: Start Training'}})
    except:
        return answer('Database not connected', 400)

    # avvio thread per addestramento elm in parallelo
    sys.path.append('./')
    import main
    x = threading.Thread(target=main.elm, args=(id,app,))
    x.start()
    ###

    return answer(result, 200)


    '''
    @app.route('/model/<id>/<output>', methods=['POST'])
    '''


@app.errorhandler(404)
def notfound(error):
    return answer('Route not found', 404)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=port)