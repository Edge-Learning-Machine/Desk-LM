import sys
import json
import argparse
import zipfile
import os
import requests
from config import *


# def elm_manager(id, app, database, model):
def elm_manager(value, database, id, app):

    # configurazione dei file json
    # app.logger.info("JSON file creation for elm")

    for element in value['model']:
        with open(f'{os.getenv("INPUT_PATH")}{element}_api.json','w') as file:
            json.dump(value['model'][element], file, indent=4)

    # for element in api_json_files:
    #     with open(f'{os.getenv("INPUT_PATH")}{element}_api.json','w') as file:
    #         if element in model['model']:
    #             json.dump(model['model'][element], file, indent=4)

    # aggiorno il database
    error, code = database.update_one(os.getenv('MODELS_COLLECTION'), {'_id':id}, {'$set':{'status':model_status[3]}})
    if error:
        app.logger.error(error)
        return

    # try:
    #     collection.update_one({'_id':id}, {'$set':{'status':status[3]}})
    # except:
    #     app.logger.info(api_errors['no_db'])

    sys.path.append('./')
    from main import ELM

    # configurazione args per elm
    parser = argparse.ArgumentParser()
    parser.add_argument('--predict')
    parser.add_argument('--store', action="store_true")
    args = parser.parse_args()

    args.dataset = f'{os.getenv("INPUT_PATH")}ds_api.json'
    args.preprocess = f'{os.getenv("INPUT_PATH")}pp_api.json'
    args.estimator = f'{os.getenv("INPUT_PATH")}est_api.json'
    args.selection = f'{os.getenv("INPUT_PATH")}ms_api.json'
    args.output = f'{os.getenv("INPUT_PATH")}output_api.json'

    # inizializzazione di elm
    elm = ELM.init(args)

    # elaborazione di elm
    if elm == 0:
        ELM.process()
        # aggiorno il database
        error, code = database.update_one(os.getenv('MODELS_COLLECTION'), {'_id':id}, {'$set':{'status.perc':100}})
        if error:
            app.logger.error(error)
            return
        # try:
        #     collection.update_one({'_id':id}, {'$set':{'status.perc':100}})
        # except:
        #     app.logger.error(api_errors['no_db'])
    else:
        app.logger.error(elm)
        error, code = database.update_one(os.getenv('MODELS_COLLECTION'), {'_id':id}, {'$set':{'status':{'error':str(elm)}}})
        if error:
            app.logger.error(error)
        # collection.update_one({'_id':id}, {'$set':{'error':str(elm)}})
        return
    
    #creazione zip
    with zipfile.ZipFile(value['output'], 'w') as f:
        for root, dirs, files in os.walk(os.getenv('OUTPUT_PATH')):
            for file in files:
                f.write(os.path.join(root, file))

    #aggiorno mongodb
    error, code = database.update_one(os.getenv('MODELS_COLLECTION'), {'_id':id}, {'$set':{'status':model_status[4]}})
    if error:
        app.logger.error(error)
        return
    # try:
    #     collection.update_one({'_id':id}, {'$set':{'status':status[4]}})
    # except:
    #     app.logger.error(api_errors['no_db'])

    app.logger.info("Done training")

    #webhook
    if 'webhook' in value:
        app.logger.info('Sending status to ' + value['webhook'])
        requests.get(value['webhook'])