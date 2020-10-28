import json
import jsonschema
from jsonschema import validate

import abc

import error as error
from Estimator import Estimator
import sys
sys.path.insert(1, 'utils')
import dict_utils


class SVM(Estimator):
    def __init__(self, jsonData):
        super().__init__()
        self.nick = 'svm'
        try:
            with open('schemas/svmSchema.json') as schema_file:
                svmSchema = json.load(schema_file)
        except FileNotFoundError as err:
            template = "An exception of type {0} occurred. Arguments: {1!r}"
            message = template.format(type(err).__name__, err.args)
            print(message)
            raise ValueError(error.errors['svm_config'])
        try:
            validate(instance=jsonData, schema=svmSchema)
        except jsonschema.exceptions.ValidationError as err:
            template = "An exception of type {0} occurred. Arguments: {1!r}"
            message = template.format(type(err).__name__, err.args)
            print(message)
            raise ValueError(error.errors['svm_config'])
        self.parse(jsonData)

    def parse(self, jsonData):
        if jsonData['estimator'] == 'LinearSVC':
            from sklearn.svm import LinearSVC
            self.estimator = LinearSVC(random_state=0)
            self.is_regr = False
        elif jsonData['estimator'] == 'LinearSVR':
            from sklearn.svm import SVR
            self.estimator = SVR(kernel='linear')
            self.is_regr = True
        self.params = {}

        self.params['C'] = dict_utils.parse_related_properties('C_exp', jsonData, 0, is_exp=True)
        '''
        if 'C' in jsonData:
            self.params['C'] = [jsonData['C']]
        elif 'C_lower_exp' in jsonData and 'C_upper_exp' in jsonData:
            import numpy as np
            l = jsonData['C_lower_exp']
            u = jsonData['C_upper_exp']
            self.params['C'] = np.logspace(l, u, u-l+1)
        elif 'C_lower_exp' in jsonData:
            self.params['C'] = [jsonData['C_lower_exp']]
        elif 'C_upper_exp' in jsonData:
            self.params['C'] = [jsonData['C_upper_exp']]
        else:
            self.params['C'] = 1
        '''

        import sys
        sys.path.insert(1, 'output')
        import SVM_OM
        self.output_manager = SVM_OM.SVM_OM(self)
