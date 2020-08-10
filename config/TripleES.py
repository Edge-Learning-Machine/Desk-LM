import json
import jsonschema
from jsonschema import validate

import abc

import error as error
from Estimator import Estimator
import sys

import numpy as np                               # vectors and matrices
import pandas as pd                              # tables and data manipulations

from dateutil.relativedelta import relativedelta # working with dates with style
from scipy.optimize import minimize              # for function minimization

import statsmodels.formula.api as smf            # statistics and econometrics
import statsmodels.tsa.api as smt
import statsmodels.api as sm
import scipy.stats as scs

from itertools import product                    # some useful functions
from tqdm import tqdm_notebook

import warnings                                  # `do not disturbe` mode
warnings.filterwarnings('ignore')

# Describe what kind of json you expect.
tripleESSchema = {
    "type": "object",
    "properties": {
        "estimator": {
            "type": "string"
            },
        "season_length": {
            "type": "number"
            },
        "scaling_factor": {
            "type": "number"
            }
    },
    "required": ["estimator", "season_length"],
    "additionalProperties": False
}

class TripleES(Estimator):
    def __init__(self, jsonData):
        super().__init__()
        self.nick = 'tripleES'
        try:
            validate(instance=jsonData, schema=tripleESSchema)
        except jsonschema.exceptions.ValidationError as err:
            template = "An exception of type {0} occurred. Arguments: {1!r}"
            message = template.format(type(err).__name__, err.args)
            print(message)
            raise ValueError(error.errors['tripleES_config'])
        self.parse(jsonData)
        self.estimator = self
        

    def parse(self, jsonData):
        self.is_regr = True
        
        if 'scaling_factor' in jsonData: 
            self.scaling_factor = jsonData['scaling_factor']
        else:
            self.scaling_factor = 1.96    
        self.season_length = jsonData['season_length']   
            
        sys.path.insert(1, 'output')
        import TripleES_OM
        self.output_manager = TripleES_OM.TripleES_OM(self)

    def process(self, prep, cv, X_train, y_train):
    # initializing model parameters alpha, beta and gamma
        x = [0, 0, 0] 

    # Minimizing the loss function 
        from scipy.optimize import minimize
        from sklearn.metrics import mean_squared_error, mean_squared_log_error

        #leggiamo cv.metrics, a seconda del suo valore stringa gli passo l'oggetto corrispondente        
        if 'mean_squared_log_error' in cv.metrics:
            abg = minimize(timeseriesCVscore, x0=x, 
                args=(X_train, cv.cv, mean_squared_log_error, self.season_length),
                method="TNC", bounds = ((0, 1), (0, 1), (0, 1))
                )
        elif 'mean_squared_error' in cv.metrics: #usable also for rootMSE
            abg = minimize(timeseriesCVscore, x0=x, 
                args=(X_train, cv.cv, mean_squared_error, self.season_length),
                method="TNC", bounds = ((0, 1), (0, 1), (0, 1))
                )
        else:
            template = "An exception of type {0} occurred. Arguments: {1!r}"
            message = template.format('Wrong metrics configuration parameter', cv.metrics)
            raise ValueError(message)

    # Take optimal values...
        #best_estimator = abg.x
 
        self.alpha = abg.x[0]
        self.beta = abg.x[1]
        self.gamma = abg.x[2]  
        self.X_train = X_train     
        #return best_estimator # stimatore deve restituire alpha, beta e gamma
        return self

    def predict(self, X_test):
        self.model = HoltWinters(self.X_train, self.season_length, self.alpha, self.beta, self.gamma, len(X_test), self.scaling_factor) 
        self.model.triple_exponential_smoothing()
        predictions = self.model.result[-len(X_test):]
        return predictions

class HoltWinters:
    
    """
    Holt-Winters model with the anomalies detection using Brutlag method
    
    # series - initial time series
    # slen - length of a season <- parametro da mettere nel json est_tscv
    # alpha, beta, gamma - Holt-Winters model coefficients <- output paramas
    # n_preds - predictions horizon <- parametro def a priori
    # scaling_factor - sets the width of the confidence interval by Brutlag (usually takes values from 2 to 3) <- ? può essere
    hyperparmas per CV
    
    """
    def __init__(self, series, slen, alpha, beta, gamma, n_preds, scaling_factor=1.96):
        self.series = series
        self.slen = slen
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.n_preds = n_preds
        self.scaling_factor = scaling_factor
        
        
    def initial_trend(self):
        sum = 0.0
        for i in range(self.slen):
            sum += float(self.series[i+self.slen] - self.series[i]) / self.slen
        return sum / self.slen  
    
    def initial_seasonal_components(self):
        seasonals = {}
        season_averages = []
        n_seasons = int(len(self.series)/self.slen)
        # let's calculate season averages
        for j in range(n_seasons):
            season_averages.append(sum(self.series[self.slen*j:self.slen*j+self.slen])/float(self.slen))
        # let's calculate initial values
        for i in range(self.slen):
            sum_of_vals_over_avg = 0.0
            for j in range(n_seasons):
                sum_of_vals_over_avg += self.series[self.slen*j+i]-season_averages[j]
            seasonals[i] = sum_of_vals_over_avg/n_seasons
        return seasonals   

          
    def triple_exponential_smoothing(self):
        self.result = []
        self.Smooth = []
        self.Season = []
        self.Trend = []
        self.PredictedDeviation = []
        
        seasonals = self.initial_seasonal_components()
        
        for i in range(len(self.series)+self.n_preds):
            if i == 0: # components initialization
                smooth = self.series[0]
                trend = self.initial_trend()
                self.result.append(self.series[0])
                self.Smooth.append(smooth)
                self.Trend.append(trend)
                self.Season.append(seasonals[i%self.slen])
                
                self.PredictedDeviation.append(0)
                
                continue
                
            if i >= len(self.series): # predicting
                m = i - len(self.series) + 1
                self.result.append((smooth + m*trend) + seasonals[i%self.slen])
                
                # when predicting we increase uncertainty on each step
                self.PredictedDeviation.append(self.PredictedDeviation[-1]*1.01) 
                
            else:
                val = self.series[i]
                last_smooth, smooth = smooth, self.alpha*(val-seasonals[i%self.slen]) + (1-self.alpha)*(smooth+trend)
                trend = self.beta * (smooth-last_smooth) + (1-self.beta)*trend
                seasonals[i%self.slen] = self.gamma*(val-smooth) + (1-self.gamma)*seasonals[i%self.slen]
                self.result.append(smooth+trend+seasonals[i%self.slen])
                
                # Deviation is calculated according to Brutlag algorithm.
                self.PredictedDeviation.append(self.gamma * np.abs(self.series[i] - self.result[i]) 
                                               + (1-self.gamma)*self.PredictedDeviation[-1])
                     
            self.Smooth.append(smooth)
            self.Trend.append(trend)
            self.Season.append(seasonals[i%self.slen])


from sklearn.model_selection import TimeSeriesSplit 
from sklearn.metrics import mean_squared_error
def timeseriesCVscore(params, series, cv, loss_function, slen):
    """
        Returns error on CV  
        
        params - vector of parameters for optimization
        series - dataset with timeseries
        slen - season length for Holt-Winters model
    """
    # errors array
    errors_arr = []
    
    values = series.values
    alpha, beta, gamma = params
    
    # set the number of folds for cross-validation
    tscv = TimeSeriesSplit(n_splits=cv)

    # iterating over folds, train model on each, forecast and calculate error
    for train, test in tscv.split(values):        
        try:
            n=len(train)-2*slen
            assert n > 0
        except AssertionError as err:
            template = "An exception of type {0} occurred"
            message = template.format(type(err).__name__)
            print(message)
            raise ValueError(error.errors['tripleES_wrong_nsplits'])
        
        model = HoltWinters(series=values[train], slen=slen, 
                            alpha=alpha, beta=beta, gamma=gamma, n_preds=len(test))
        model.triple_exponential_smoothing()
        
        predictions = model.result[-len(test):]
        actual = values[test]
        error_arr = loss_function(predictions, actual)
        errors_arr.append(error_arr)
        
    return np.mean(np.array(errors_arr))
