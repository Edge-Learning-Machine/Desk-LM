import unittest 
import jsonpickle
import json
from dotenv import load_dotenv
from api import app
from commons.error import *

class TestServer(unittest.TestCase): 

    def setUp(self):
        load_dotenv(dotenv_path='api/variables.env')
        self.app = app.test_client()
        self.app.testing = True

    def test_post_model_errors_no_token(self):
        result = self.app.post('/model')
        self.assertEqual(result.status_code, api_errors['auth']['status'])
        result = jsonpickle.decode(result.data)
        self.assertEqual(result['type'], api_errors['auth']['type'])

    def test_post_model_errors_no_contents(self):
        result = self.app.post('/model', headers={
            'Authorization': '1a832e85-7dda-4240-9c0c-42d9adbe09fa',
            'content_type': 'application/json'
        })
        self.assertEqual(result.status_code, api_errors['request']['status'])
        result = jsonpickle.decode(result.data)
        self.assertEqual(result['type'], api_errors['request']['type'])
        self.assertEqual(result['details'], 'No request content')

    def test_post_model_errors_no_json(self):
        result = self.app.post('/model',
            headers={'Authorization': '1a832e85-7dda-4240-9c0c-42d9adbe09fa'}, 
            data=json.dumps({'text':'test'}))
        self.assertEqual(result.status_code, api_errors['request']['status']) 
        result = jsonpickle.decode(result.data)
        self.assertEqual(result['type'], api_errors['request']['type'])
        self.assertEqual(result['details'], 'Request content not in JSON format')

    def test_post_model_errors_validation(self):
        result = self.app.post('/model',
            headers={'Authorization': '1a832e85-7dda-4240-9c0c-42d9adbe09fa','content_type': 'application/json'}, 
            json={})
        self.assertEqual(result.status_code, api_errors['validation']['status']) 
        result = jsonpickle.decode(result.data)
        self.assertEqual(result['type'], api_errors['validation']['type'])
    
if __name__ == '__main__':
    unittest.main()