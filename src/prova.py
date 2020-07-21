import time
from pymongo import MongoClient
import requests
from flask import Flask, request, jsonify, send_file, Response

def prova(id, app=None, collection=None):

    app.logger.info("Start ELM training")
    collection.update_one({'_id':id}, {'$set':{'status':"2: Training...0%"}})

    ### HERE ELM
    time.sleep(10)
    ###

    app.logger.info("End ELM training")
    collection.update_one({'_id':id}, {'$set':{'status':"2: Training...100%"}})
    
    ###
    result = collection.find_one({'_id':id})
    if 'webhook' in result:
        requests.get(result.webhook)

    return 0