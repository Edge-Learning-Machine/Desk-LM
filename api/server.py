import markdown
import markdown.extensions.fenced_code
import markdown.extensions.codehilite
from pygments.formatters import HtmlFormatter
from flask import Flask, request, send_file


def server(database):
    app = Flask(__name__)
    
    @app.route('/model', methods=['GET'])
    def get_models():
        from routes.get_models_route import get_models_route
        return get_models_route(request, database)

    @app.route('/model/<id>', methods=['GET'])
    def get_model(id):
        from routes.get_model_route import get_model_route
        return get_model_route(request, database, id)

    @app.route('/model', methods=['POST'])
    def post_model():
        from routes.post_model_route import post_model_route
        return post_model_route(request, database)

    @app.route('/model/<id>/trainingset', methods=['POST'])
    def post_model_trainingset(id):
        from routes.post_model_trainingset_route import post_model_trainingset_route
        return post_model_trainingset_route(request, database, id)

    @app.route('/model/<id>', methods=['PUT'])
    def put_model(id):
        from routes.put_model_route import put_model_route
        return put_model_route(request, database, id, app)

    @app.route('/model/<id>/output', methods=['GET'])
    def get_model_download(id):
        from routes.get_model_download_route import get_model_download_route
        return get_model_download_route(request, database, id)

    @app.route('/model/<id>', methods=['DELETE'])
    def delete_model(id):
        from routes.delete_model_route import delete_model_route
        return delete_model_route(request, database, id)

    @app.errorhandler(404)
    def notfound(error):
        return bad(api_errors['route'])

    return app