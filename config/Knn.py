import json
import jsonschema
from jsonschema import validate

import abc

import error as error
from Estimator import Estimator


class Knn(Estimator):
    def __init__(self, jsonData):
        super().__init__()
        self.nick = 'knn'
        try:
            with open('schemas/knnSchema.json') as schema_file:
                knnSchema = json.load(schema_file)
        except FileNotFoundError as err:
            template = "An exception of type {0} occurred. Arguments: {1!r}"
            message = template.format(type(err).__name__, err.args)
            print(message)
            raise ValueError(error.errors['knn_config'])
        try:
            validate(instance=jsonData, schema=knnSchema)
        except jsonschema.exceptions.ValidationError as err:
            template = "An exception of type {0} occurred. Arguments: {1!r}"
            message = template.format(type(err).__name__, err.args)
            print(message)
            raise ValueError(error.errors['knn_config'])
        self.parse(jsonData)

    def parse(self, jsonData):
        if jsonData['estimator'].endswith('Classifier'):
            from sklearn.neighbors import KNeighborsClassifier
            self.estimator = KNeighborsClassifier()
            self.is_regr = False
        else:
            from sklearn.neighbors import KNeighborsRegressor
            self.estimator = KNeighborsRegressor()
            self.is_regr = True
        self.params = {}
        
        import sys
        sys.path.insert(1, 'utils')
        import dict_utils
        self.params['n_neighbors'] = dict_utils.parse_related_properties('n_neighbors', jsonData, 5)
        
        sys.path.insert(1, 'output')
        import Knn_OM #as Knn_OM
        self.output_manager = Knn_OM.Knn_OM(self)
