import json
import jsonschema
from jsonschema import validate

import error as error

# Describe what kind of json you expect.
cvSchema = {
    "type": "object",
    "properties": {
        "cv": {
            "type": "number"
            },
        "scoring": {
            "type": "string"
            },
        "verbose": {
            "type": "number"
            }
    },
    # "required": ["cv"],
    "additionalProperties": False
}

class ModelSelection(object):

    # Constructor
    def __init__(self, jsonFilePath, estimator):
        self.cv = None
        self.verbose = 0
        if jsonFilePath != None:
            try:
                with open(jsonFilePath) as json_file:
                    try:
                        jsonData = json.load(json_file)                               
                        validate(instance=jsonData, schema=cvSchema)
                    except jsonschema.exceptions.ValidationError as err:
                        template = "An exception of type {0} occurred. Arguments: {1!r}"
                        message = template.format(type(err).__name__, err.args)
                        print(message)
                        raise ValueError(error.errors['modelselection_config'])
                    except ValueError as err:
                        template = "An exception of type {0} occurred. Arguments: {1!r}"
                        message = template.format(type(err).__name__, err.args)
                        print(message)
                        raise ValueError(error.errors['modelselection_config'])
                    self.parse(jsonData, estimator)
            except FileNotFoundError as err:
                    template = "An exception of type {0} occurred. Arguments: {1!r}"
                    message = template.format(type(err).__name__, err.args)
                    print(message)
                    raise ValueError(error.errors['modelselection_config'])
        else:
            self.assign_default_values(estimator)

    def parse(self, jsonData, estimator):
        if 'cv' in jsonData:
            self.cv = jsonData['cv']
        self.process_scoring_param(jsonData, estimator)      

    def process_scoring_param(self, jsonData, estimator):
        import sklearn.metrics as metrics
        
        if 'verbose' in jsonData:
            self.verbose = jsonData['verbose']            
        if 'scoring' in jsonData:
            self.scoring = jsonData['scoring']
            if estimator.is_regr:
                if self.scoring in ['mean_absolute_error', 'mean_squared_error', 'mean_squared_log_error']:
                    self.metrics = self.scoring
                    self.scoring = 'neg_' + self.scoring
                elif self.scoring in ['root_mean_squared_error']:
                    self.metrics = 'mean_squared_error'
                    self.is_RMSE = True
                    self.scoring = 'neg_' + self.scoring
                elif self.scoring in ['r2']:
                    self.metrics = self.scoring + '_score'
                else:
                    raise ValueError(error.errors['unknown_scoring_attribute'] + ' ' + self.scoring)
            else:
                if self.scoring in ['accuracy', 'balanced_accuracy']: #, 'average_precision']:
                    self.metrics = self.scoring + '_score'
                else:
                    sl = self.scoring.split('_')
                    if sl[0] in ['f1', 'precision', 'recall']:
                        self.metrics = sl[0] + '_score'
                        if len(sl)>1:
                            if sl[1] in ['micro', 'macro', 'samples', 'weighted']:
                                self.metrics_average = sl[1]
                            elif sl[1] == 'binary' and estimator.n_classes == 2:
                                 self.metrics_average = 'binary'
                            elif estimator.n_classes == 2:
                                self.metrics_average = 'binary'
                            else:
                                self.metrics_average = 'weighted'
                        elif estimator.n_classes == 2:
                            self.metrics_average = 'binary'
                        else:
                            self.scoring = self.scoring + '_weighted'
                            self.metrics_average = 'weighted'
                    else:
                        raise ValueError(error.errors['unknown_scoring_attribute'] + ' ' + self.scoring)
        else:
            self.assign_default_values(estimator)

    def assign_default_values(self, estimator):
        self.scoring = None
        if estimator.is_regr:
            if estimator.nick == 'ann':
                self.metrics = 'mean_squared_error' #'r2_score'
            else:
                self.metrics = 'r2_score'
        else:
            self.metrics = 'accuracy_score'