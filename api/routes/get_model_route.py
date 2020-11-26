import os
from commons.error import *
from commons.checker import *
from commons.response import *


def get_model_route(request, database, id):
     # check authorization
    try: 
        check_authorization(database, request.headers.get('Authorization'))
    except:
        return bad(api_errors['auth'])
    
     # get model from the database
    try:
        doc = database.find_one(os.getenv('MODELS_COLLECTION'),{'_id':id})
    except ValueError as error:
        return bad(error)

    return answer(doc)