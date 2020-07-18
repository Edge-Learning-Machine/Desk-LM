import time
import markdown
import json
import jsonpickle
import markdown.extensions.fenced_code
import markdown.extensions.codehilite
import os
from flask import Flask, request, jsonify, send_file, Response
from pymongo import MongoClient
import uuid
from datetime import datetime
import threading
import sys

app = Flask(__name__)
port = int(os.environ.get('PORT', 5000))
client = MongoClient('localhost', 27017)
db = client['elm']
models = db['models']

model_parameters = ['e','p','s','o','webhook']


def answer(content, status):
    if(status != 200):
        content = { 'error': content }
    return jsonify(content), status



@app.route('/model', methods=['POST'])
def model():
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
        models.insert_one(content)
    except:
        return answer('Database not connected', 400)
    #...

    return answer(content, 200)


@app.route('/model/<id>', methods=['GET'])
def get_model(id):
    try:
        result = models.find_one({'_id':id})
    except:
        return answer('Database not connected', 400)
    if not result:
        return answer('Model not existing in the database', 400)

    return answer(result, 200)


@app.route('/model/<id>', methods=['DELETE'])
def delete_model(id):
    try:
        result = models.find_one({'_id':id})
    except:
        return answer('Database not connected', 400)
    if not result:
        return answer('Model not existing in the database', 400)

    if result['d']['path']:
        try:
            os.remove(result['d']['path'])
        except:
            return answer("Error in deleting csv file", 400)

    try:
        models.delete_one({'_id':id})
    except:
        return answer("Error in deleting model", 400)

    return answer("Model deleted", 200)


@app.route('/model/<id>/trainingset', methods=['POST'])
def training(id):    
    if not request.files.get('file'):
        return answer("Missing .csv file", 400)
    
    if not request.form.get('target_column'):
        return answer("Missing target_column parameter", 400)

    try:
        result = models.find_one({'_id':id})
    except:
        return answer('Database not connected', 400)

    if not result:
        return answer("Model not existing in the database", 400)

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
    if request.form.get('skip_rows'):
        result['d']['skip_rows'] = request.form.getlist('skip_rows')
    if request.form.get('skip_columns'):
        result['d']['skip_columns'] = request.form.getlist('skip_columns')
    if request.form.get('sep'):
        result['d']['sep'] = request.form.get('sep')
    if request.form.get('decimal'):
        result['d']['decimal'] = request.form.get('decimal')
    if request.form.get('test_size'):
        result['d']['test_size'] = request.form.get('test_size')
    if request.form.get('categorical_multiclass'):
        result['d']['categorical_multiclass'] = request.form.get('categorical_multiclass')
    
    result['status'] = '1: CSV uploaded'
    try:
        models.update_one({'_id':id}, {'$set':result})
    except:
        return answer("Database not connected", 400)
    #...

    return answer(result, 200)


@app.route('/model/<id>', methods=['PUT'])
def put(id):
    if (not request.data):
        return answer('No request contents', 400)
    if (not request.is_json):
        return answer('Request content not in JSON format', 400)
    try:
        jsonpickle.decode(request.data)
    except ValueError as e:
        return answer('Request format not in valid JSON: ' + e, 400)

    try:
        result = models.find_one({'_id':id})
    except:
        return answer('Database not connected', 400)

    if not result:
        return answer("Model not existing in the database", 400)

    content = request.get_json()

    if not content['evaluate']:
        return answer("Evaluate must be true to begin training", 400)

    result = models.update_one({'_id':id}, {'$set':{'status':'2: Start Training'}})
    # avvio thread per addestramento elm
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
    app.run(debug=True, host='localhost', port=port)