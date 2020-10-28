import json
import jsonschema
from jsonschema import validate

import os

import error as error


class Predict(object):

    # Constructor
    def __init__(self, jsonFilePath):
        try:
            with open('schemas/predictSchema.json') as schema_file:
                predictSchema = json.load(schema_file)
        except FileNotFoundError as err:
            template = "An exception of type {0} occurred. Arguments: {1!r}"
            message = template.format(type(err).__name__, err.args)
            print(message)
            raise ValueError(error.errors['predict_config'])
        try:
            with open(jsonFilePath) as json_file:
                try:
                    jsonData = json.load(json_file)            
                    validate(instance=jsonData, schema=predictSchema)
                except jsonschema.exceptions.ValidationError as err:
                    template = "An exception of type {0} occurred. Arguments: {1!r}"
                    message = template.format(type(err).__name__, err.args)
                    print(message)
                    raise ValueError(error.errors['predict_config'])
                except ValueError as err:
                    template = "An exception of type {0} occurred. Arguments: {1!r}"
                    message = template.format(type(err).__name__, err.args)
                    print(message)
                    raise ValueError(error.errors['predict_config'])
                self.parse(jsonData)
        except FileNotFoundError as err:
                template = "An exception of type {0} occurred. Arguments: {1!r}"
                message = template.format(type(err).__name__, err.args)
                print(message)
                raise ValueError(error.errors['predict_config'])

    def parse(self, jsonData):
        try:
            self.model_id = jsonData['model_id']
            self.samples = jsonData['samples']
            if 'n_preds' in jsonData:
                self.n_preds = jsonData['n_preds']
        except Exception as err:
            template = "An exception of type {0} occurred. Arguments: {1!r}"
            message = template.format(type(err).__name__, err.args)
            print(message)
            raise ValueError(error.errors['predict_config'])