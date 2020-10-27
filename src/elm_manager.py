import os
import sys
import json
import argparse
import zipfile
import requests
from commons.status import *
from jsonschema import validate

def reset_elm_config(elm):
    elm.predict = None
    elm.dataset = None
    elm.estimator = None
    elm.preprocess = None
    elm.modelselection = None
    elm.output = None

    elm.training_set_cap = None
    elm.args = None
    elm.uuid_str = None
    return


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

        # inizializzazione di elm
        reset_elm_config(ELM)
        elm = ELM.init(args)

        # elimino il file di storage creato precedentemente (ne verrà creato uno nuovo)
        if 'storage' in value:
            if os.path.isfile('storage/' + value['storage'] + '.pkl'):
                os.remove('storage/' + value['storage'] + '.pkl')

        if elm == 0:
            # elaborazione di elm
            ELM.process()

            # aggiorno il database
            error = database.update_one(os.getenv('MODELS_COLLECTION'), {'_id':id}, {'$set':{'status.perc':100,'storage':ELM.uuid_str}})
            if error:
                app.logger.error(error)
                return
        else:
            app.logger.error(elm)
            error = database.update_one(os.getenv('MODELS_COLLECTION'), {'_id':id}, {'$set':{'status.error':str(elm)}})
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

        # configurazione dei file json
        predict = {
            'model_id': value['storage'],
            'samples': content['samples']
        }
        with open(f'{os.getenv("INPUT_PATH")}pr_api.json','w') as file:
            json.dump(predict, file, indent=4)

        sys.path.append('./')
        from main import ELM

        # inizializzazione di elm
        reset_elm_config(ELM)
        elm = ELM.init(args)

        if elm == 0:
            # elaborazione di elm
            result = ELM.process()
            app.logger.info("Done predict")
            return result
        else:
            # app.logger.error(elm)
            return elm
