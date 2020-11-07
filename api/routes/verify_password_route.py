import os
from commons.error import *
from werkzeug.security import check_password_hash, generate_password_hash

users = {
    "Administrator": generate_password_hash("administrator")
}

def verify_password_route(database, username, password):
    error, value = database.find_one(os.getenv('CLIENTS_COLLECTION'),{'username':username,'password':generate_password_hash(password)})
    if not error:
        if value:
            return username
    # error, value = database.find_one(os.getenv('CLIENTS_COLLECTION'),{'username':username})
    # if error:
    #     return error, 404
    # if not value:
    #     return api_errors['no_user'], 401
    # return  username