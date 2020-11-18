import os
import sys
import json
import argparse
import zipfile
import requests
from commons.status import *
from jsonschema import validate

sys.path.append('./')
from main import ELM

def elm_manager(app, content, database, doc, mode, **kargs):
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

    if mode=='evaluate':
        # configurazione args per elm in modalità 'evaluate'
        args.dataset = f'{os.getenv("INPUT_PATH")}ds_api.json'
        args.preprocess = f'{os.getenv("INPUT_PATH")}pp_api.json'
        args.estimator = f'{os.getenv("INPUT_PATH")}est_api.json'
        args.selection = f'{os.getenv("INPUT_PATH")}ms_api.json'
        args.output = f'{os.getenv("INPUT_PATH")}output_api.json'
        args.store = True

        app.logger.info("Start training")

        # configurazione e creazione dei file json
        for element in doc['model']:
            with open(f'{os.getenv("INPUT_PATH")}{element}_api.json','w') as file:
                json.dump(doc['model'][element], file, indent=4)

        # elm start
        try:
            elm = ELM(args)
            elm.process(model_id=doc['_id'])
        except ValueError as error:
            app.logger.error(error)
            # aggiorno il database
            try:
                database.update_one(os.getenv('MODELS_COLLECTION'), {'_id':doc['_id']}, {'$set':{'status.error':str(error)}})
            except ValueError as error:
                app.logger.error(error)
            return
        
        # creazione zip output
        with zipfile.ZipFile(os.getenv('ZIP_PATH') + '/' + doc['_id'] + '.zip', 'w') as f:
            for root, dirs, files in os.walk(os.getenv('OUTPUT_PATH')):
                for file in files:
                    f.write(os.path.join(root, file))

        # aggiorno il database
        try:
            database.update_one(os.getenv('MODELS_COLLECTION'), {'_id':doc['_id']}, {'$set':{'status':model_status[3]}})
        except ValueError as error:
            app.logger.error(error)
            return

        app.logger.info("Done training")

        # send webhook
        if kargs['webhook']:
            if not 'headers' in kargs['webhook']: kargs['webhook']['headers'] = {}
            if not 'data' in kargs['webhook']: kargs['webhook']['data'] = {}

            app.logger.info(f'Sending webhook to: {kargs["webhook"]["url"]}')
            try:
                requests.request(kargs['webhook']['method'], kargs['webhook']['url'], 
                        headers=kargs['webhook']['headers'], data=kargs['webhook']['data'])
            except:
                app.logger.error("Webhook not send")

    elif mode=='predict':
        # configurazione args per elm in modalità 'predict'
        args.predict = f'{os.getenv("INPUT_PATH")}pr_api.json'

        app.logger.info("Start predict")

        # salvataggio del file json
        with open(f'{os.getenv("INPUT_PATH")}pr_api.json','w') as file:
            json.dump(content, file, indent=4)

        # elm start 
        try:
            elm = ELM(args)
            predict = elm.process()
        except ValueError as err:
            app.logger.error(err)
            raise ValueError(err)

        app.logger.info("Done predict")
        return predict

    elif mode=='measurify':
        # configurazione args per elm in modalità 'evaluate'
        args.dataset = kargs['dataset']
        args.columns = kargs['columns']
        args.target = kargs['target']
        args.preprocess = f'{os.getenv("INPUT_PATH")}pp_api.json'
        args.estimator = f'{os.getenv("INPUT_PATH")}est_api.json'
        args.selection = f'{os.getenv("INPUT_PATH")}ms_api.json'
        args.output = f'{os.getenv("INPUT_PATH")}output_api.json'
        args.store = True

        app.logger.info("Start training")

        # configurazione e creazione dei file json
        for element in doc['model']:
            with open(f'{os.getenv("INPUT_PATH")}{element}_api.json','w') as file:
                json.dump(doc['model'][element], file, indent=4)

        # elm start
        try:
            elm = ELM(args)
            elm.process(model_id=doc['_id'])
        except ValueError as error:
            app.logger.error(error)
            # aggiorno il database
            try:
                database.update_one(os.getenv('MODELS_COLLECTION'), {'_id':doc['_id']}, {'$set':{'status.error':str(error)}})
            except ValueError as error:
                app.logger.error(error)
            return

        # creazione zip output
        with zipfile.ZipFile(os.getenv('ZIP_PATH') + '/' + doc['_id'] + '.zip', 'w') as f:
            for root, dirs, files in os.walk(os.getenv('OUTPUT_PATH')):
                for file in files:
                    f.write(os.path.join(root, file))

        # aggiorno il database
        try:
            database.update_one(os.getenv('MODELS_COLLECTION'), {'_id':doc['_id']}, {'$set':{'status':model_status[2]}})
        except ValueError as error:
            app.logger.error(error)
            return

        app.logger.info("Done training")


        # send webhook
        if kargs['webhook']:
            if not 'headers' in kargs['webhook']: kargs['webhook']['headers'] = kargs['headers']
            if not 'data' in kargs['webhook']: kargs['webhook']['data'] = {'code':'model'}

            app.logger.info(f'Sending webhook to: {kargs["webhook"]["url"]}')
            try:
                requests.request(kargs['webhook']['method'], kargs['webhook']['url'], 
                        headers=kargs['webhook']['headers'], json=kargs['webhook']['data'], verify=False)
            except:
                app.logger.error("Webhook not send")