import markdown
import markdown.extensions.fenced_code
import markdown.extensions.codehilite
from pygments.formatters import HtmlFormatter
from flask import Flask, request, send_file
# from flask_httpauth import HTTPBasicAuth
from controllers.modelControllers import *


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




    # auth = HTTPBasicAuth()

    # @auth.login_required
    # def login():
    #     return jsonify({ 'data': 'Hello, %s!' % g.user.username})

    # @auth.verify_password
    # def verify_password(username, password):
    #     user = User.query.filter_by(username = username).first()
    #     if not user or not user.verify_password(password):
    #         return False
    #     g.user = user
    #     return True

    # @auth.verify_password
    # def verify_password(username, password):
    #     from routes.verify_password_route import verify_password_route
    #     return verify_password_route(database, username, password)

    # @auth.verify_token
    # def verify_token(token):
    #     pass

    # @app.route('/login', methods=['POST'])
    # def login_route():
    #     from routes.login_route import login_route
    #     return login_route(request, database)
    # @app.route('/stream', methods=['POST'])
    # def upload_dataset():

    #     while True:
    #         chunk = request.stream.read(4096)
    #         print(chunk)
    #         if len(chunk) == 0:
    #             break
    #     # with open(app.root_path + "/tmp/current_dataset", "bw") as f:
    #     #     chunk_size = 4096
    #     #     while True:
    #     #         chunk = request.stream.read(chunk_size)
    #     #         if len(chunk) == 0:
    #     #             return

    #     #         f.write(chunk)
    #     return answer("OK", 200)