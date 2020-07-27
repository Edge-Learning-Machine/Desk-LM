import sys
import json
import argparse
import zipfile
import os

INPUT = 'input/'
#INPUT = '/input/'
API_JSON_FILES = ['ds','pp','est','ms','output']

def int_elm(id, app, collection, model, path, status, api_errors):

    #configurazione dei file json
    app.logger.info("JSON file creation for elm")

    '''
    for element in model['model']:
        with open(f'{INPUT}{element}_api.json', 'w') as file:
            json.dump(model['model'][element], file, indent=4)
    '''

    for element in API_JSON_FILES:
        with open(f'{INPUT}{element}_api.json','w') as file:
            if element in model['model']:
                json.dump(model['model'][element], file, indent=4)

    #aggiorno mongodb
    try:
        collection.update_one({'_id':id}, {'$set':{'status':status[3]}})
    except:
        app.logger.info(api_errors['no_db'])

    sys.path.append('./')
    from main import ELM

    parser = argparse.ArgumentParser()
    parser.add_argument('--predict')
    parser.add_argument('--store', action="store_true")
    args = parser.parse_args()

    args.dataset = f'{INPUT}ds_api.json'
    args.preprocess = f'{INPUT}pp_api.json'
    args.estimator = f'{INPUT}est_api.json'
    args.selection = f'{INPUT}ms_api.json'
    args.output = f'{INPUT}output_api.json'

    elm = ELM.init(args)
    if elm == 0:
        ELM.process()
        #aggiorno mongodb
        try:
            collection.update_one({'_id':id}, {'$set':{'status.perc':100}})
        except:
            app.logger.info(api_errors['no_db'])
    else:
        app.logger.info(elm)
        collection.update_one({'_id':id}, {'$set':{'error':str(elm)}})
        return
    
    #creazione zip
    with zipfile.ZipFile(path['zip'] + model['output'], 'w') as f:
        for root, dirs, files in os.walk(path['output']):
            for file in files:
                f.write(os.path.join(root, file))

    #aggiorno mongodb
    try:
        collection.update_one({'_id':id}, {'$set':{'status':status[4]}})
    except:
        app.logger.info(api_errors['no_db'])

    app.logger.info("Done training")

    return 