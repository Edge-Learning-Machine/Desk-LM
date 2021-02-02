import os
import numpy
import requests
import threading
import pandas as pd
from commons.error import *
from commons.status import *
from commons.checker import *
from commons.response import *
from commons.measurify import *

def put_model_route(request, database, id, app):
    # check authorization
    try: 
        check_authorization(database, request.headers.get('Authorization'))
    except:
        return bad(api_errors['auth'])

    # check json format
    try:
        content = check_json(request)
    except ValueError as error:
        return bad(error)

    # check request params
    try:
        check_schema(content, f'{os.getenv("SCHEMAS_PATH")}putSchema.json')
    except ValueError as error:
        return bad(error)

    # get model from the database
    try:
        doc = database.find_one(os.getenv('MODELS_COLLECTION'),{'_id':id})
    except ValueError as error:
        return bad(error)

    # select the mode
    if content['mode'] == 'evaluate':
        # check 'dataset' param
        if not doc['dataset']:
            error = api_errors['invalid']
            error['details'] = 'Missing dataset'
            return bad(error)

        # status and database updates
        doc['status'] = Status.TRAINING.value
        if 'error' in doc: del doc['error']

        try:
            database.replace_one(os.getenv('MODELS_COLLECTION'), {'_id':doc['_id']}, doc)
        except ValueError as error:
            return bad(error)

        # start training elm (thread)
        from elm_manager import elm_manager
        elm_thread_evaluate = threading.Thread(
            target=elm_manager, 
            args=(app, content, database, doc, 'evaluate', ),
            kwargs={'webhook':doc['webhook'],})
        elm_thread_evaluate.start()

        return answer(doc)

    elif content['mode'] == 'predict':
        # check 'status' param
        if doc['status'] != Status.CONCLUDED.value:
            error = api_errors['invalid']
            error['details'] = 'Wait for the training'
            return bad(error)

        # set elm params
        del content['mode']
        content['model_id'] = doc['_id']

        # check predict params
        try: 
            check_schema(content, f'{os.getenv("SCHEMAS_PATH")}predictSchema.json')
        except ValueError as error:
            return bad(error)
            
        # start prediction elm 
        from elm_manager import elm_manager
        try:
            result = elm_manager(app, content, database, doc, 'predict')
            if isinstance(result, numpy.ndarray): 
                result = result.tolist()
            return answer({"predict": result})
        except ValueError as error:
            return bad(error)

    elif content['mode'] == 'measurify':
        # create Dataset
        try:
            # get token from Measurify
            headers = { 'Authorization': postLogin() }

            # get items of the feature
            res = getResource('features', content['feature'], {}, headers)

            columns = []
            for item in res['items']:
                if item['name'] in content['items']:
                    columns.append(item['name'])
            columns.append('target')

            ds = {}
            for item in res['items']:
                ds[item['name']] = []
            ds['target'] = []

            # filter
            filter = json.loads(content['filter'])
            filter['$or'] = []
            for tag in content['tags']:
                filter['$or'].append({"tags":tag})

            params = {}
            params['filter'] = json.dumps(filter)
            params['page'] = 1

            while True:
                response = getResources('measurements', params, headers, True)
                for document in response['docs']:
                    for sample in document['samples']:
                        for i, v in enumerate(sample['values']):
                            ds[res['items'][i]['name']].append(v)
                        ds['target'].append(document['tags'][0])
                if not response['nextPage']: break 
                params['page'] += 1

            dataset = pd.DataFrame(ds, columns=columns)
            dataset[['target']] = dataset[['target']].apply(lambda col: pd.Categorical(col).codes)

            # webhook
            if doc['webhook']:
                data = { 'progress': 50 }
                app.logger.info(f'Sending webhook ({doc["webhook"]["method"]}) to: {doc["webhook"]["url"]}')
                try:
                    requests.request(doc['webhook']['method'], doc['webhook']['url'], 
                            headers=headers, json=data, verify=False)
                except:
                    app.logger.error("Webhook not send")

        except Exception as e:
            error = api_errors['measurify']
            error['details'] = str(e)
            return bad(error)
    
        # start training elm with dataset (thread)
        from elm_manager import elm_manager
        elm_thread_measurify = threading.Thread(
            target=elm_manager, 
            args=(app, content, database, doc, 'measurify', ),
            kwargs={'dataset':dataset, 'columns':columns, 'target':'target', 'webhook':doc['webhook'], 'headers':headers})
        elm_thread_measurify.start()

        return answer(doc)