import unittest 
import jsonpickle
import json
from server import app

class TestServer(unittest.TestCase): 

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_post_model_errors_no_contents(self):
        result = self.app.post('/model', content_type='application/json')
        self.assertEqual(result.status_code, 400)
        result = jsonpickle.decode(result.data)
        self.assertEqual(result['error'], 'No request contents', 'Should be No request contents')

    def test_post_model_errors_no_json(self):
        result = self.app.post('/model', data=json.dumps({'text':'test'}))
        self.assertEqual(result.status_code, 400) 
        result = jsonpickle.decode(result.data)
        self.assertEqual(result['error'], 'Request content not in JSON format')

    def test_post_model_errors_missing_parameter_e(self):
        result = self.app.post('/model', content_type='application/json', data=json.dumps({'text':'test'}))
        self.assertEqual(result.status_code, 400)
        result = jsonpickle.decode(result.data)
        self.assertEqual(result['error'], "Missing parameter: 'e'")

    def test_post_model_errors_missing_parameter_p(self):
        result = self.app.post('/model', content_type='application/json', data=json.dumps({'e':{}}))
        self.assertEqual(result.status_code, 400)
        result = jsonpickle.decode(result.data)
        self.assertEqual(result['error'], "Missing parameter: 'p'")

    def test_post_model_errors_missing_parameter_s(self):
        result = self.app.post('/model', content_type='application/json', data=json.dumps({'e':{},'p':{}}))
        self.assertEqual(result.status_code, 400)
        result = jsonpickle.decode(result.data)
        self.assertEqual(result['error'], "Missing parameter: 's'")

    def test_post_model_errors_missing_parameter_o(self):
        result = self.app.post('/model', content_type='application/json', data=json.dumps({'e':{},'p':{},'s':{}}))
        self.assertEqual(result.status_code, 400)
        result = jsonpickle.decode(result.data)
        self.assertEqual(result['error'], "Missing parameter: 'o'")

    def test_post_model_errors_missing_parameter_webhook(self):
        result = self.app.post('/model', content_type='application/json', data=json.dumps({'e':{},'p':{},'s':{},'o':{}}))
        self.assertEqual(result.status_code, 400)
        result = jsonpickle.decode(result.data)
        self.assertEqual(result['error'], "Missing parameter: 'webhook'")

if __name__ == '__main__':
    unittest.main()