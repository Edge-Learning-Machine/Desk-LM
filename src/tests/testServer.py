import unittest 
import jsonpickle
import json
from server import app

class TestServer(unittest.TestCase): 

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_post_model_errors_no_token(self):
        result = self.app.post('/model')
        self.assertEqual(result.status_code, 400)
        result = jsonpickle.decode(result.data)
        self.assertEqual(result['error'], 'Missing token')

    def test_post_model_errors_no_auth(self):
        result = self.app.post('/model', headers={'Authorization':'Invalid token'})
        self.assertEqual(result.status_code, 401)
        result = jsonpickle.decode(result.data)
        self.assertEqual(result['error'], 'Unauthorizated')

    def test_post_model_errors_no_contents(self):
        result = self.app.post('/model', headers={
            'Authorization': 'Token di prova',
            'content_type': 'application/json'
        })
        self.assertEqual(result.status_code, 400)
        result = jsonpickle.decode(result.data)
        self.assertEqual(result['error'], 'No request contents', 'Should be No request contents')

    def test_post_model_errors_no_json(self):
        result = self.app.post('/model', headers={'Authorization': 'Token di prova'}, data=json.dumps({'text':'test'}))
        self.assertEqual(result.status_code, 400) 
        result = jsonpickle.decode(result.data)
        self.assertEqual(result['error'], 'Request content not in JSON format')
    
if __name__ == '__main__':
    unittest.main()