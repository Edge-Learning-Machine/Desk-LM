from flask import jsonify
import json
import pickle

def answer(content):
    return jsonify(content), 200

def bad(error):
    if isinstance(error, ValueError):
        error = error.args[0]
    return jsonify(error), error['status']