from flask import jsonify

def answer(content, status):
    if(status != 200):
        content = { 'error': content }
    return jsonify(content), status