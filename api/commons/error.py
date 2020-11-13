# api_errors = {
#     'no_user': 'Incorrect username or password',
#     'no_token': 'Missing token',
#     'no_db': 'Database not found',
#     'no_auth': 'Unauthorizated',
#     'no_req': 'No request contents',
#     'no_json': 'Request content not in JSON format',
#     'no_json_valid': 'Request format not in valid JSON',
#     'no_params': 'Invalid model params',
#     'no_model': 'Model not found',
#     'no_csv': 'Missing csv file',
#     'no_save': 'Error uploading file csv',
#     'no_train': 'Model not trained yet',
#     'no_mode': 'Please, choose a mode',
#     'wrong_mode': 'mode not yet available'
# }

api_errors = {
    'route': { 'status': 404, 'type': 'Route error', 'details': 'Route not found'},
    'generic': { 'status': 400, 'type': 'Generic error' },
    'auth': { 'status': 401, 'type': 'Unauthorized'},
    'database': { 'status': 400, 'type': 'Database error' },
    'request': { 'status': 400, 'type': 'Request error'},
    'notfound': { 'status': 400, 'type': 'Not found error'},
    'validation': { 'status': 400, 'type': 'Validation error'},
    'invalid': { 'status': 400, 'type': 'Invalid model error'},
    'measurify': { 'status': 400, 'type': 'Measurify error' }
}