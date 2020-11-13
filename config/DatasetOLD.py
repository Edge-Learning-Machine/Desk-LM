import json
import jsonschema
from jsonschema import validate

import os

import numpy as np
import pandas as pd
import error as error


class Dataset(object):

    # Constructor
    def __init__(self, jsonFilePath):
        try:
            with open('schemas/dsSchema.json') as schema_file:
                datasetSchema = json.load(schema_file)
        except FileNotFoundError as err:
            template = "An exception of type {0} occurred. Arguments: {1!r}"
            message = template.format(type(err).__name__, err.args)
            print(message)
            raise ValueError(error.errors['ds_config'])
        try:
            with open(jsonFilePath) as json_file:
                try:
                    jsonData = json.load(json_file)            
                    validate(instance=jsonData, schema=datasetSchema)
                except jsonschema.exceptions.ValidationError as err:
                    template = "An exception of type {0} occurred. Arguments: {1!r}"
                    message = template.format(type(err).__name__, err.args)
                    print(message)
                    raise ValueError(error.errors['ds_config'])
                except ValueError as err:
                    template = "An exception of type {0} occurred. Arguments: {1!r}"
                    message = template.format(type(err).__name__, err.args)
                    print(message)
                    raise ValueError(error.errors['ds_config'])
                self.parse(jsonData)
                base = os.path.basename(jsonFilePath)
                self.name = os.path.splitext(base)[0]
        except FileNotFoundError as err:
                template = "An exception of type {0} occurred. Arguments: {1!r}"
                message = template.format(type(err).__name__, err.args)
                print(message)
                raise ValueError(error.errors['ds_config'])

    def parse(self, jsonData):
        try:
            skiprows = None
            if 'skip_rows' in jsonData:
                skiprows = jsonData['skip_rows']
            if 'sep' in jsonData:
                sep = jsonData['sep']
            else:
                sep = ','
            if 'decimal' in jsonData:
                decimal = jsonData['decimal']
            else:
                decimal = '.'
            dfr = pd.read_csv(jsonData['path'], skiprows=skiprows, sep=sep, decimal=decimal)
            dfr.columns = map(str.lower, dfr.columns)
            if 'time_series_column' in jsonData:
                tsc = jsonData['time_series_column'].lower()
                self.X = dfr[tsc]
                self.y = dfr[tsc]
            elif 'select_columns' in jsonData:
                sfc = jsonData['select_columns']
                sfc = [s.lower() for s in sfc]
                self.X = dfr[sfc]
                if 'target_column' in jsonData:
                    tc = jsonData['target_column'].lower()
                    self.y = dfr.loc[:,tc]
                else:
                    self.y = dfr.iloc[:,-1]
            elif 'skip_columns' in jsonData:
                skc = jsonData['skip_columns']
                skc = [s.lower() for s in skc]
                dfr.drop(skc, axis = 1, inplace = True)
                if 'target_column' in jsonData:
                    tc = jsonData['target_column'].lower()
                    self.y = dfr.loc[:,tc]
                    self.X = dfr.drop(tc, axis = 1)
                else:
                    self.y = dfr.iloc[:,-1]
                    self.X = dfr.drop(dfr.columns[-1], axis = 1)

            # Imputation
            #self.X.replace(r'^\s*$', np.nan, regex=True, inplace=True)           
            #self.X = self.X.apply(lambda x: x.fillna(x.mean()),axis=0)
            #self.X.fillna(self.X.mean(), inplace=True)

            if 'test_size' in jsonData:
                self.test_size = jsonData['test_size']
            else:
                self.test_size = 0.3
            if 'categorical_multiclass' in jsonData:
                self.is_categorical_multiclass = jsonData['categorical_multiclass']
            else:
                self.is_categorical_multiclass = False

        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments: {1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print(message)
            raise ValueError(error.errors['ds_config'])

    def one_hot_encode(self):
        if self.is_categorical_multiclass:
            from sklearn.preprocessing import LabelEncoder
            from keras.utils import np_utils
            # encode class values as integers
            encoder = LabelEncoder()
            encoder.fit(self.y)
            encoded_y = encoder.transform(self.y)
            # convert integers to dummy variables (i.e. one hot encoded)
            self.y = np_utils.to_categorical(encoded_y)