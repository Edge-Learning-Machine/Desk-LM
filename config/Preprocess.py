import json
import jsonschema
from jsonschema import validate
import error as error
from sklearn import preprocessing


possible_scalers = {
    'StandardScaler':preprocessing.StandardScaler(),
    #'RobustScaler':preprocessing.RobustScaler(),
    'MinMaxScaler':preprocessing.MinMaxScaler(),
    #'QuantileScaler':preprocessing.QuantileTransformer()
}


class Preprocess(object):
    # Constructor
    def __init__(self, jsonFilePath):
        self.scalers = []
        self.pca_values = []
        
        try:
            with open('schemas/ppSchema.json') as schema_file:
                preprocessSchema = json.load(schema_file)
        except FileNotFoundError as err:
            template = "An exception of type {0} occurred. Arguments: {1!r}"
            message = template.format(type(err).__name__, err.args)
            print(message)
            raise ValueError(error.errors['preprocess_config'])

        if jsonFilePath != None:
            try:
                with open(jsonFilePath) as json_file:
                    try:
                        jsonData = json.load(json_file)
                        validate(instance=jsonData, schema=preprocessSchema)
                    except jsonschema.exceptions.ValidationError as err:
                        template = "An exception of type {0} occurred. Arguments: {1!r}"
                        message = template.format(type(err).__name__, err.args)
                        print(message)
                        raise ValueError(error.errors['preprocess_config'])
                    except ValueError as err:
                        template = "An exception of type {0} occurred. Arguments: {1!r}"
                        message = template.format(type(err).__name__, err.args)
                        print(message)
                        raise ValueError(error.errors['preprocess_config'])
                    self.parse(jsonData)
            except FileNotFoundError as err:
                    template = "An exception of type {0} occurred. Arguments: {1!r}"
                    message = template.format(type(err).__name__, err.args)
                    print(message)
                    raise ValueError(error.errors['preprocess_config'])

    def parse(self, jsonData):
        if jsonData['scale']!=None:
            for scaler in jsonData['scale']:
                if scaler in possible_scalers:
                    self.scalers.append(possible_scalers[scaler])
                else:
                    print(f'Scaler: {scaler}, not recognized')
        if 'pca_values' in jsonData:
            self.pca_values = jsonData['pca_values']