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

    app.run(debug=False, host=host, port=port, ssl_context=('src/resources/cert.pem', 'src/resources/key.pem'))

# import time
# import markdown
# import markdown.extensions.fenced_code
# import markdown.extensions.codehilite
# import json
# import jsonpickle
# import os
# from pygments.formatters import HtmlFormatter
# from datetime import datetime
# import sys