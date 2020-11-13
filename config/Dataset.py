import os
import json
import jsonschema
from jsonschema import validate

import numpy as np
import pandas as pd 
import error as error


class Dataset:

    def __init__(self, *args):
        if len(args) == 1:
            self.jsonData = self.__validate_schema(args[0])
            df = self.__open_csv(self.jsonData)
        elif len(args) == 3:
            df = args[0]
            self.jsonData = {}
            self.jsonData['select_columns'] = args[1]
            self.jsonData['target_column'] = args[2]

        df.columns = map(str.lower, df.columns)
        self.__parse(df)

    def __parse(self, dfr):
        try:
            if 'time_series_column' in self.jsonData:
                tsc = jsonData['time_series_column'].lower()
                self.X = dfr[tsc]
                self.y = dfr[tsc]
            elif 'select_columns' in self.jsonData:
                sfc = self.jsonData['select_columns']
                sfc = [s.lower() for s in sfc]
                self.X = dfr[sfc]
                if 'target_column' in self.jsonData:
                    tc = self.jsonData['target_column'].lower()
                    self.y = dfr.loc[:,tc]
                else:
                    self.y = dfr.iloc[:,-1]
            elif 'skip_columns' in self.jsonData:
                skc = self.jsonData['skip_columns']
                skc = [s.lower() for s in skc]
                dfr.drop(skc, axis = 1, inplace = True)
                if 'target_column' in self.jsonData:
                    tc = self.jsonData['target_column'].lower()
                    self.y = dfr.loc[:,tc]
                    self.X = dfr.drop(tc, axis = 1)
                else:
                    self.y = dfr.iloc[:,-1]
                    self.X = dfr.drop(dfr.columns[-1], axis = 1)

            # Imputation
            #self.X.replace(r'^\s*$', np.nan, regex=True, inplace=True)           
            #self.X = self.X.apply(lambda x: x.fillna(x.mean()),axis=0)
            #self.X.fillna(self.X.mean(), inplace=True)
            
            if 'test_size' in self.jsonData:
                self.test_size = self.jsonData['test_size']
            else:
                self.test_size = 0.3
            if 'categorical_multiclass' in self.jsonData:
                self.is_categorical_multiclass = self.jsonData['categorical_multiclass']
            else:
                self.is_categorical_multiclass = False

        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments: {1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print(message)
            raise ValueError(error.errors['ds_config'])

    def __validate_schema(self, jsonFilePath):
        try:
            with open('schemas/dsSchema.json') as schema_file:
                datasetSchema = json.load(schema_file)

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
                return jsonData
        except FileNotFoundError as err:
            template = "An exception of type {0} occurred. Arguments: {1!r}"
            message = template.format(type(err).__name__, err.args)
            print(message)
            raise ValueError(error.errors['ds_config'])

    def __open_csv(self, jsonData):
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
            return dfr
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