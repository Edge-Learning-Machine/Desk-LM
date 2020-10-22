# base_token = 'src/BASE_TOKEN.json'

# database = {
#     "url": "mongodb://mongodb:27017/", 
#     "name": "elm",
#     "collections": [
#         "clients",
#         "models"
#     ]
# }

# api_json_files = ['ds','pp','est','ms','output']

# path = {
#     "datasets": "datasets/",
#     "input": "input/",
#     "output": "out/",
#     "zip": "zip/"
# }

model_status = [
    { 'code': 0, 'description': 'Model uploaded'},
    { 'code': 1, 'description': 'File csv uploaded'},
    { 'code': 2, 'description': 'Send to elm'},
    { 'code': 3, 'description': 'Training', 'perc': 0},
    { 'code': 4, 'description': 'Done'}
]

api_errors = {
    'no_token': 'Missing token',
    'no_db': 'Database not found',
    'no_auth': 'Unauthorizated',
    'no_req': 'No request contents',
    'no_json': 'Request content not in JSON format',
    'no_json_valid': 'Request format not in valid JSON',
    'no_model': 'Model not found',
    'no_csv': 'Missing csv file',
    'no_save': 'Error uploading file csv',
    'no_train': 'Model not trained yet'
}