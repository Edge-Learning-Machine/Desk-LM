import json
import jsonschema
from jsonschema import validate

import abc

import error as error
from Estimator import Estimator


class DecisionTree(Estimator):
    def __init__(self, jsonData):
        super().__init__()
        self.nick = 'dt'
        try:
            with open('schemas/dtSchema.json') as schema_file:
                dtSchema = json.load(schema_file)
        except FileNotFoundError as err:
            template = "An exception of type {0} occurred. Arguments: {1!r}"
            message = template.format(type(err).__name__, err.args)
            print(message)
            raise ValueError(error.errors['dt_config'])
        try:
            validate(instance=jsonData, schema=dtSchema)
        except jsonschema.exceptions.ValidationError as err:
            template = "An exception of type {0} occurred. Arguments: {1!r}"
            message = template.format(type(err).__name__, err.args)
            print(message)
            raise ValueError(error.errors['dt_config'])
        self.parse(jsonData)

    def parse(self, jsonData):
        if jsonData['estimator'].endswith('Classifier'):
            from sklearn.tree import DecisionTreeClassifier
            self.estimator = DecisionTreeClassifier(criterion='gini')
            self.is_regr = False
        elif jsonData['estimator'].endswith('Regressor'):
            from sklearn.tree import DecisionTreeRegressor
            self.estimator = DecisionTreeRegressor(criterion='mse')
            self.is_regr = True
        else:
            print(f'Invalid value for estimator name: {jsonData["estimator"]}')
            raise ValueError(error.errors['estimator_config'])
        self.params = {}
        
        import sys
        sys.path.insert(1, 'utils')
        import dict_utils
        self.params['max_depth'] = dict_utils.parse_related_properties('max_depth', jsonData, None)
        self.params['min_samples_split'] = dict_utils.parse_related_properties('min_samples_split', jsonData, 2)
        self.params['min_samples_leaf'] = dict_utils.parse_related_properties('min_samples_leaf', jsonData, 1)
        self.params['max_leaf_nodes'] = dict_utils.parse_related_properties('max_leaf_nodes', jsonData, None)
        
        sys.path.insert(1, 'output')
        import DecisionTree_OM
        self.output_manager = DecisionTree_OM.DecisionTree_OM(self)