import json
import jsonschema
from jsonschema import validate

import abc

import error as error
from Estimator import Estimator

#from ModelSelection import ModelSelection

from keras.layers import Dense, Dropout
from keras.models import Model, Sequential

import numpy as np


class ANN(Estimator):
    def __init__(self, jsonData):
        super().__init__()
        self.nick = 'ann'
        try:
            with open('schemas/annSchema.json') as schema_file:
                annSchema = json.load(schema_file)
        except FileNotFoundError as err:
            template = "An exception of type {0} occurred. Arguments: {1!r}"
            message = template.format(type(err).__name__, err.args)
            print(message)
            raise ValueError(error.errors['ann_config'])
        try:
            validate(instance=jsonData, schema=annSchema)
        except jsonschema.exceptions.ValidationError as err:
            template = "An exception of type {0} occurred. Arguments: {1!r}"
            message = template.format(type(err).__name__, err.args)
            print(message)
            raise ValueError(error.errors['ann_config'])
        self.parse(jsonData)

    def parse(self, jsonData):
        if jsonData['estimator'].endswith('Classifier'):
            from keras.wrappers.scikit_learn import KerasClassifier
            #self.estimator = KerasClassifier()
            self.is_regr = False
        else:
            from keras.wrappers.scikit_learn import KerasRegressor
            #self.estimator = KerasRegressor()
            self.is_regr = True
        self.params = {}
        
        import sys
        sys.path.insert(1, 'utils')
        import dict_utils
        self.params['epochs'] = dict_utils.parse_related_properties('epochs', jsonData, 10)
        self.params['batch_size'] = dict_utils.parse_related_properties('batch_size', jsonData, 32)
        self.params['dropout'] = dict_utils.parse_related_properties('dropout', jsonData, 0, is_float=True)
        #self.params['activation'] = dict_utils.parse_related_properties('activation', jsonData, ['relu'])
        
        #self.params['min_samples_leaf'] = dict_utils.parse_related_properties('min_samples_leaf', jsonData, 1)
        #self.params['max_leaf_nodes'] = dict_utils.parse_related_properties('max_leaf_nodes', jsonData, None)
        if 'activation' in jsonData:
            self.activation = jsonData['activation']
        else:
            self.activation = ['relu']
        if 'hidden_layers' in jsonData:
            self.hidden_layers = jsonData['hidden_layers']
        else:
            self.hidden_layers = []
        sys.path.insert(1, 'output')
        import ANN_OM
        self.output_manager = ANN_OM.ANN_OM(self)

    def process(self, prep, cv, X_train, y_train):
        param_grid = self.createGrid(prep)

        scoring_from_cv = (cv != None) and (cv.scoring != None)
        best_score = -100000
        best_esti = None
        #mods = [(30, 5), (30, 20, 10)]
        #mods = [(10, 5)]
        from keras.wrappers.scikit_learn import KerasClassifier, KerasRegressor
        for hls in self.hidden_layers:
            hls = tuple(hls)
            for a in self.activation:
                if not self.is_regr:
                    self.estimator = KerasClassifier(build_fn=self.create_model, activation=a, hidden_layers=hls, scoring_from_cv=scoring_from_cv, verbose=0) #Regressor
                else:
                    self.estimator = KerasRegressor(build_fn=self.create_model, activation=a, hidden_layers=hls, scoring_from_cv=scoring_from_cv, verbose=0)
                #self.estimator = KerasClassifier(build_fn=self.create_model2)
                pipe = self.createPipe(prep)
                grid = self.fitGrid(pipe, param_grid, cv, X_train, y_train)
                print(grid.best_score_)
                best_params = grid.best_params_
                best_params['hidden_layers'] = hls
                best_params['activation'] = a
                print(best_params)
                if grid.best_score_ > best_score:
                    best_esti = grid.best_estimator_
        self.estimator = best_esti['esti'] # This should be useless
        return best_esti

    def create_model(self, activation='relu', hidden_layers=(7, 6), scoring_from_cv=False, dropout=0):
        model = Sequential()

        for hl in hidden_layers:
            model.add(Dense(hl, activation=activation))
            model.add(Dropout(dropout))

        if self.is_regr == True:
            model.add(Dense(1))
            loss = 'mean_squared_error'
            # metric = 'mean_squared_error'
        elif self.n_classes <= 2:
            model.add(Dense(1, activation='sigmoid'))
            loss = 'binary_crossentropy' 
            # metric = 'accuracy' #'binary_accuracy' does not work
        else:
            if self.dataset.is_categorical_multiclass:
                model.add(Dense(self.n_classes, activation='softmax'))
                loss = 'categorical_crossentropy'
                # metric = 'categorical_accuracy'
            else:
                model.add(Dense(1))
                loss = 'sparse_categorical_crossentropy'
                # metric = 'accuracy'
        
        #if (self.cv != None) and (self.cv.scoring != None):
        if scoring_from_cv:
            model.compile(loss=loss,optimizer='adam')#, metrics=[metric]) 
        elif self.is_regr == False:
            model.compile(loss=loss,optimizer='adam', metrics=['accuracy'])
        else:
            model.compile(loss=loss,optimizer='adam', metrics=['mean_squared_error']) 


        return model

    def assign_dataset(self, dataset):
        super().assign_dataset(dataset)
        #if dataset.is_categorical_multiclass:
        #    dataset.one_hot_encode()

'''
    def create_model(self, activation='relu', hidden_layers=(7, 6), dropout=0):
        model = Sequential()
        model.add(Dense(64, activation=activation))
        model.add(Dropout(dropout))

        for hl in hidden_layers:
            model.add(Dense(hl, activation=activation))

        model.add(Dense(1, activation='sigmoid'))

        #model.compile(loss='binary_crossentropy',optimizer=optimizer, metrics=['accuracy'])
        ############## Accuracy and loss
        model.compile(loss='binary_crossentropy',optimizer='adam', metrics=['accuracy'])

        return model
'''