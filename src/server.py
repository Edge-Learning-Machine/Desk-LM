from flask import Flask, request, send_file
from controllers.modelControllers import *

def server(database):
    app = Flask(__name__)
    host = 'localhost'
    port = 5000

    @app.route('/model', methods=['GET'])
    def get_models():
        return get_models_route(request, database)

    @app.route('/model/<id>', methods=['GET'])
    def get_model(id):
        return get_model_route(request, database, id)


    @app.route('/model', methods=['POST'])
    def post_model():
        return post_model_route(request, database)

    @app.route('/model/<id>/trainingset', methods=['POST'])
    def post_model_trainingset(id):
        return post_model_trainingset_route(request, database, id)

    @app.route('/model/<id>', methods=['PUT'])
    def put_model(id):
        return put_model_route(request, database, id, app)

    @app.route('/model/<id>/download', methods=['GET'])
    def get_model_download(id):
        return get_model_download_route(request, database, id)

    @app.route('/model/<id>', methods=['DELETE'])
    def delete_model(id):
        return delete_model_route(request, database, id)

    @app.errorhandler(404)
    def notfound(error):
        return answer('Route not found', 404)

    app.run(debug=True, host=host, port=port, ssl_context=('src/resources/cert.pem', 'src/resources/key.pem'))

# import time
# import markdown
# import markdown.extensions.fenced_code
# import markdown.extensions.codehilite
# import json
# import jsonpickle
# import os
# from pygments.formatters import HtmlFormatter
# from flask import Flask, request, jsonify, send_file, Response
# from pymongo import MongoClient
# import uuid
# from datetime import datetime
# import threading
# import sys
# from config import *

# #creazone app flask
# app = Flask(__name__)
# host = 'localhost'
# port = 5000

# #connessione al database
# clientDB = MongoClient(database['url'])
# cursor = clientDB[database['name']]
# clients = cursor[database['collections'][0]]
# models = cursor[database['collections'][1]]

# #creazione cartelle
# os.makedirs(path['datasets'], exist_ok=True)
# os.makedirs(path['zip'], exist_ok=True)


# def answer(content, status):
#     if(status != 200):
#         content = { 'error': content }
#     return jsonify(content), status

# def check_authorization(request):
#     if not request.headers.get('Authorization'):
#         return answer(api_errors['no_token'], 400)
#     try:
#         client = clients.find_one({'token':request.headers['Authorization']})
#     except:
#         return answer(api_errors['no_db'], 404)

#     if not client:
#         return answer(api_errors['no_auth'], 401)

# def check_json(request):
#     if (not request.data):
#         return answer(api_errors['no_req'], 400)
#     if (not request.is_json):
#         return answer(api_errors['no_json'], 400)
#     try:
#         jsonpickle.decode(request.data)
#     except ValueError as e:
#         return answer(api_errors['no_json_valid'] + ': ' + e, 400)
    

# @app.route('/model', methods=['POST'])
# def set_model():
#     # verifico che utente sia autorizzato
#     authentication = check_authorization(request)
#     if authentication:
#         return authentication

#     #verifico che la richiesta sia presente e in formato JSON valido
#     valid = check_json(request)
#     if valid: 
#         return valid

#     content = request.get_json()

#     # verifico che richiesta abbia tutti i campi necessari
#     '''
#     model_parameters = ['pp','est','ms','output']
#     for parameter in model_parameters:
#         if not parameter in content:
#             return answer("Missing parameter: '" + parameter + "'", 400)
#     '''
#     #creazione nuovo modello
#     new_model = {}
#     new_model['model'] = content

#     #aggiungo valori in risposta
#     new_model['_id'] = str(uuid.uuid4())
#     new_model['status'] = status[0]
#     new_model['output'] = new_model['_id'] +'.zip'
#     new_model['timestamp'] = str(datetime.now())

#     #sposto webhook fuori dal model
#     if 'webhook' in content:
#         new_model['webhook'] = new_model['model']['webhook']
#         del new_model['model']['webhook']

#     #inserisco in mongodb
#     try:
#         models.insert_one(new_model)
#     except Exception as e:
#         return answer(e, 404)

#     return answer(new_model, 200)


# @app.route('/model/<id>', methods=['GET'])
# def get_model(id):
#     #verifico che utente sia autorizzato
#     ca = check_authorization(request)
#     if ca: return ca

#     #recupero modello da mongo
#     try:
#         result = models.find_one({'_id':id})
#     except:
#         return answer(api_errors['no_db'], 404)

#     if not result:
#         return answer(api_errors['no_model'], 400)

#     return answer(result, 200)


# @app.route('/model/<id>/trainingset', methods=['POST'])
# def upload_csv(id):
#     #verifico che utente sia autorizzato
#     authentication = check_authorization(request)
#     if authentication:
#         return authentication

#     #verifico che vi sia il file csv allegato
#     if not request.files.get('file'):
#         return answer("Missing csv file", 400)
    
#     #verifico che vi siano i parametri necessari
#     '''
#     model_parameters = ['target_column','test_size']
#     for parameter in model_parameters:
#         if not parameter in request.form:
#             return answer("Missing parameter: '" + parameter + "'", 400)
#     '''

#     #recupero da mongodb 
#     try:
#         result = models.find_one({'_id':id})
#     except:
#         return answer(api_errors['no_db'], 404)

#     #se id non esiste
#     if not result:
#         return answer(api_errors['no_model'], 400)

#     #Salva il file csv con il nuovo nome
#     try:
#         file_name = result['_id']+'.csv'
#         f = request.files['file']
#         file_path = os.path.join(path['datasets'], file_name)
#         f.save(file_path)
#     except Exception as e:
#         app.logger.error(e);
#         return answer("Error uploading file csv", 400)


#     #aggiungo configurazione dataset
#     result['model']['ds'] = {}
#     result['model']['ds']['path'] = path['datasets'] + file_name
    
#     #aggiungo altri parametri
#     for item in request.form:
#         result['model']['ds'][item] = json.loads(request.form[item])
    
#     #aggiorno lo stato
#     result['status'] = status[1]

#     #aggiorno mongodb
#     try:
#         models.update_one({'_id':id}, {'$set':result})
#     except:
#         return answer(api_errors['no_db'], 404)

#     return answer(result, 200)


# @app.route('/model/<id>', methods=['PUT'])
# def training(id):
#     #verifico che utente sia autorizzato    
#     authentication = check_authorization(request)
#     if authentication:
#         return authentication

#     #verifico che la richiesta sia presente e in formato JSON valido
#     valid = check_json(request)
#     if valid: 
#         return valid

#     content = request.get_json()

#     #recupero modello da mongodb
#     try:
#         result = models.find_one({'_id':id})
#     except:
#         return answer(api_errors['no_db'], 404)

#     #verifico che modello esista
#     if not result:
#         return answer(api_errors['no_model'], 400)

#     #e che sia stato inserito il trainingset
#     if result['status']['code'] < 1:
#         return answer('You must first load the training set', 400)

#     #verifico body
#     if not content['evaluate']:
#         return answer("Evaluate must be true to begin training", 400)

#     #aggiorno stato e mongodb
#     try:
#         models.update_one({'_id':id}, {'$set':{'status':status[2]}})
#         result = models.find_one({'_id':id})
#     except:
#         return answer(api_errors['no_db'], 404)

#     # avvio thread per addestramento elm in parallelo
#     from iELM import iELM
#     thread = threading.Thread(target=iELM, args=(id, app, models, result, path, status, api_errors, ))
#     thread.start()

#     return answer(result, 200)


# @app.route('/model/<id>/<output>', methods=['GET'])
# def download(id, output):
#     #verifico che utente sia autorizzato    
#     authentication = check_authorization(request)
#     if authentication:
#         return authentication
    
#     #recupero modello da mongodb
#     try:
#         result = models.find_one({'_id':id})
#     except:
#         return answer(api_errors['no_db'], 404)

#     #verifico che modello sia addestrato
#     if result['status']['code'] != 4:
#         return answer("Model not trained yet", 400)

#     path_zip = '../' + path['zip'] + output

#     return send_file(path_zip, as_attachment=True)


# @app.errorhandler(404)
# def notfound(error):
#     return answer('Route not found', 404)


# if __name__ == '__main__':
#     try:
#         results = clients.find({})
#         if len(list(results)) == 0:
#             print("API initialization")
#             client = json.load(open(base_token))
#             clients.insert_one(client)
#     except Exception as e:
#         print(e)
#         quit(api_errors['no_db'])

#     app.run(debug=True, host=host, port=port, ssl_context=('src/resources/cert.pem', 'src/resources/key.pem'))