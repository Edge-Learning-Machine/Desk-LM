import os
import sys
import enum
import json
import argparse
import zipfile
import requests
from commons.status import *
from jsonschema import validate

sys.path.append('./')
from main import ELM

argument = {
    'dataset': 'ds',
    'estimator': 'est',
    'preprocess': 'pp',
    'selection': 'ms',
    'output': 'output',
    'predict': 'pr'
}

def elm_manager(app, content, database, doc, mode, **kargs):
    # configurazione args per elm
    parser = argparse.ArgumentParser()
    parser.add_argument('--store', action="store_true")
    args = parser.parse_args()

    if mode=='evaluate':
        app.logger.info("Start training")

        # configurazione args per elm in modalità 'evaluate'
        for index, (key, value) in enumerate(argument.items()):
            if value in doc['model']:
                with open(f'{os.getenv("INPUT_PATH")}{value}_api.json','w') as file:
                    json.dump(doc['model'][value], file, indent=4)
                args.__dict__[key] = f'{os.getenv("INPUT_PATH")}{value}_api.json'
            else:
                args.__dict__[key] = None
        args.store = True

        # elm start
        try:
            elm = ELM(args)
            process = elm.process(model_id=doc['_id'])
        except ValueError as error:
            app.logger.error(error)
            # aggiorno il database
            try:
                database.update_one(os.getenv('MODELS_COLLECTION'), {'_id':doc['_id']}, {'$set':{'status': Status.ERROR.value, 'error': str(error)}})
            except ValueError as error:
                app.logger.error(error)
            return
        
        # creazione zip output
        if args.output != None:
            with zipfile.ZipFile(os.getenv('ZIP_PATH') + '/' + doc['_id'] + '.zip', 'w') as f:
                for root, dirs, files in os.walk(os.getenv('OUTPUT_PATH')):
                    for file in files:
                        f.write(os.path.join(root, file))

        # result
        result = {
            'best_params': elm.estimator.best_params,
            'metrics': process[0],
            'score': process[-1]
        }
        if len(process) == 3: result['metrics_average'] = process[1]

        # aggiorno il database
        try:
            database.update_one(os.getenv('MODELS_COLLECTION'), {'_id':doc['_id']}, {'$set':{'status': Status.CONCLUDED.value, 'result': result}})
        except ValueError as error:
            app.logger.error(error)
            return

        app.logger.info("Done training")

        # send webhook
        if kargs['webhook']:
            if not 'headers' in kargs['webhook']: kargs['webhook']['headers'] = {}
            if not 'data' in kargs['webhook']: kargs['webhook']['data'] = {}

            app.logger.info(f'Sending webhook ({kargs["webhook"]["method"]}) to: {kargs["webhook"]["url"]}')
            try:
                requests.request(kargs['webhook']['method'], kargs['webhook']['url'], 
                        headers=kargs['webhook']['headers'], data=kargs['webhook']['data'])
            except:
                app.logger.error("Webhook not send")

    elif mode=='predict':
        app.logger.info("Start predict")

        # configurazione args per elm in modalità 'predict'
        args.predict = f'{os.getenv("INPUT_PATH")}pr_api.json'

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
        app.logger.info("Start training")

        # configurazione args per elm in modalità 'evaluate'
        for index, (key, value) in enumerate(argument.items()):
            if value in doc['model']:
                with open(f'{os.getenv("INPUT_PATH")}{value}_api.json','w') as file:
                    json.dump(doc['model'][value], file, indent=4)
                args.__dict__[key] = f'{os.getenv("INPUT_PATH")}{value}_api.json'
            else:
                args.__dict__[key] = None
        args.store = True
        args.dataset = kargs['dataset']
        args.columns = kargs['columns']
        args.target = kargs['target']

        # elm start
        try:
            elm = ELM(args)
            process = elm.process(model_id=doc['_id'])
        except ValueError as error:
            app.logger.error(error)
            # aggiorno il database
            try:
                database.update_one(os.getenv('MODELS_COLLECTION'), {'_id':doc['_id']}, {'$set':{'status': Status.ERROR.value, 'error':str(error)}})
            except ValueError as error:
                app.logger.error(error)
            return

        # creazione zip output
        if args.output != None:
            with zipfile.ZipFile(os.getenv('ZIP_PATH') + '/' + doc['_id'] + '.zip', 'w') as f:
                for root, dirs, files in os.walk(os.getenv('OUTPUT_PATH')):
                    for file in files:
                        f.write(os.path.join(root, file))

        # result
        result = {
            'best_params': elm.estimator.best_params,
            'metrics': process[0],
            'score': process[-1]
        }
        if len(process) == 3: result['metrics_average'] = process[1]

        # aggiorno il database
        try:
            database.update_one(os.getenv('MODELS_COLLECTION'), {'_id':doc['_id']}, {'$set':{'status': Status.CONCLUDED.value, 'result': result }})
        except ValueError as error:
            app.logger.error(error)
            return

        app.logger.info("Done training")


        # send webhook
        if kargs['webhook']:
            if not 'headers' in kargs['webhook']: kargs['webhook']['headers'] = kargs['headers']
            if not 'data' in kargs['webhook']: kargs['webhook']['data'] = {'progress': 100}

            app.logger.info(f'Sending webhook ({kargs["webhook"]["method"]}) to: {kargs["webhook"]["url"]}')
            try:
                requests.request(kargs['webhook']['method'], kargs['webhook']['url'], 
                        headers=kargs['webhook']['headers'], json=kargs['webhook']['data'], verify=False)
            except:
                app.logger.error("Webhook not send")