import os
import sys
import json
import argparse
import zipfile
import requests
from commons.status import *
from jsonschema import validate


def elm_manager(mode, database, id, value, app, content):
    # configurazione args per elm
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dataset')
    parser.add_argument('-p', '--preprocess')
    parser.add_argument('-e', '--estimator')
    parser.add_argument('-s', '--selection')
    parser.add_argument('-o', '--output')
    parser.add_argument('--predict')
    parser.add_argument('--store', action="store_true")
    args = parser.parse_args()

    if(mode=='evaluate'):
        # configurazione args per elm in modalità 'evaluate'
        args.dataset = f'{os.getenv("INPUT_PATH")}ds_api.json'
        args.preprocess = f'{os.getenv("INPUT_PATH")}pp_api.json'
        args.estimator = f'{os.getenv("INPUT_PATH")}est_api.json'
        args.selection = f'{os.getenv("INPUT_PATH")}ms_api.json'
        args.output = f'{os.getenv("INPUT_PATH")}output_api.json'
        args.store = True

        app.logger.info("Start training")

        # configurazione dei file json
        for element in value['model']:
            with open(f'{os.getenv("INPUT_PATH")}{element}_api.json','w') as file:
                json.dump(value['model'][element], file, indent=4)

        # aggiorno il database
        error = database.update_one(os.getenv('MODELS_COLLECTION'), {'_id':id}, {'$set':{'status':model_status[3]}})
        if error:
            app.logger.error(error)
            return

        sys.path.append('./')
        from main import ELM

        # elm start
        try:
            elm = ELM(args)
            elm.process(value['_id'])
            # aggiorno il database
            error = database.update_one(os.getenv('MODELS_COLLECTION'), {'_id':id}, {'$set':{'status.perc':100,'storage':value['_id']}})
            if error:
                app.logger.error(error)
                return
        except ValueError as err:
            app.logger.error(err)
            # aggiorno il database
            error = database.update_one(os.getenv('MODELS_COLLECTION'), {'_id':id}, {'$set':{'status.error':str(err)}})
            if error:
                app.logger.error(error)
            return
        
        # creazione zip
        with zipfile.ZipFile(value['output'], 'w') as f:
            for root, dirs, files in os.walk(os.getenv('OUTPUT_PATH')):
                for file in files:
                    f.write(os.path.join(root, file))

        # aggiorno il database
        error = database.update_one(os.getenv('MODELS_COLLECTION'), {'_id':id}, {'$set':{'status':model_status[4]}})
        if error:
            app.logger.error(error)
            return

        app.logger.info("Done training")

        # send webhook
        if 'webhook' in value:
            app.logger.info('Sending status to ' + value['webhook'])
            requests.get(value['webhook'])

    elif(mode=='predict'):
        # configurazione args per elm in modalità 'predict'
        args.predict = f'{os.getenv("INPUT_PATH")}pr_api.json'

        app.logger.info("Start predict")

        # salvataggio del file json
        with open(f'{os.getenv("INPUT_PATH")}pr_api.json','w') as file:
            json.dump(content, file, indent=4)

        sys.path.append('./')
        from main import ELM

        # elm start 
        try:
            elm = ELM(args)
            predict = elm.process()
            app.logger.info("Done predict")
            return predict
        except ValueError as err:
            app.logger.error(err)
            raise ValueError(err)
