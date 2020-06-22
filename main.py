import argparse

import logger as lg


import numpy as np

'''
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV

from keras.layers import Dense, Dropout
from keras.models import Model, Sequential
from keras.wrappers.scikit_learn import KerasRegressor

# load your data
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
X, y = load_iris(return_X_y=True)
X_train,X_test,y_train,y_test = train_test_split(
    X, y, random_state=0)

# create a function that returns a model, taking as parameters things you
# want to verify using cross-valdiation and model selection
def create_model(optimizer='adagrad',
                 kernel_initializer='glorot_uniform', 
                 dropout=0.2):
    model = Sequential()
    model.add(Dense(64,activation='relu',kernel_initializer=kernel_initializer))
    model.add(Dropout(dropout))
    model.add(Dense(1,activation='sigmoid',kernel_initializer=kernel_initializer))

    model.compile(loss='binary_crossentropy',optimizer=optimizer, metrics=['accuracy'])

    return model

# wrap the model using the function you created
clf = KerasRegressor(build_fn=create_model,verbose=0)

scaler = StandardScaler()

# create parameter grid, as usual, but note that you can
# vary other model parameters such as 'epochs' (and others 
# such as 'batch_size' too)
param_grid = {
    'clf__optimizer':['rmsprop','adam','adagrad'],
    'clf__epochs':[4,8],
    'clf__dropout':[0.1,0.2],
    'clf__kernel_initializer':['glorot_uniform','normal','uniform']
}

param_grid = {
    'clf__epochs':[10, 20]
}

pipeline = Pipeline([
    ('preprocess',scaler),
    ('clf',clf)
])

# if you're not using a GPU, you can set n_jobs to something other than 1
grid = GridSearchCV(pipeline, cv=2, param_grid=param_grid)
grid.fit(X_train, y_train)

# summarize results
print("Best: %f using %s" % (grid.best_score_, grid.best_params_))
means = grid.cv_results_['mean_test_score']
stds = grid.cv_results_['std_test_score']
params = grid.cv_results_['params']
for mean, stdev, param in zip(means, stds, params):
    print("%f (%f) with: %r" % (mean, stdev, param))
'''




parser = argparse.ArgumentParser()
parser.add_argument('-d', '--dataset')
parser.add_argument('-p', '--preprocess')
parser.add_argument('-e', '--estimator')
parser.add_argument('-s', '--selection')
parser.add_argument('-o', '--output')
args = parser.parse_args()

import sys
print("Python version")
print (sys.version)
import numpy as np
print("Numpy version")
print(np.__version__) 
import sklearn as skl
print("Sklearn version")
print(skl.__version__) 

sys.path.insert(1, 'config')
import Dataset as cds
try:
    ds = cds.Dataset(args.dataset)
except ValueError as err:
    quit(err)

import Estimator as ce
try:
    esti = ce.Estimator.create(args.estimator, ds)
except ValueError as err:
    quit(err)

import Preprocess as pp
try:
    prep = pp.Preprocess(args.preprocess)
except ValueError as err:
    quit(err)

import ModelSelection as ms
try:
    ms = ms.ModelSelection(args.selection, esti)
except ValueError as err:
    quit(err)

# lg.initLogger(args.dataset, args.estimator)

op = None
training_size = None
if args.output != None:
    import Output
    try:
        op = Output.Output(args.output)
    except ValueError as err:
        quit(err)
    if esti.nick=='knn':
        training_size = op.training_set_cap


from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(
    ds.X, ds.y, train_size=training_size, test_size=ds.test_size, random_state=0)

col_means = X_train.mean()
X_train = X_train.fillna(col_means)
X_test = X_test.fillna(col_means)

best_estimator = esti.process(prep, ms, X_train, y_train)
#print(best_estimator.score(X_test, y_test))
y_pred = best_estimator.predict(X_test)

import sklearn.metrics as metrics
if hasattr(ms, 'metrics_average'):
    score = getattr(metrics, ms.metrics)(y_test, y_pred, average=ms.metrics_average)
    print(f'{cv.metrics}, average={ms.metrics_average} in testing set: {score}')
else:
    if hasattr(ms, 'is_RMSE'):
        score = getattr(metrics, ms.metrics)(y_test, y_pred, squared=not ms.is_RMSE)
        pref = ''
        if ms.is_RMSE:
            pref='root_'
        print(f'{pref}{ms.metrics} in testing set: {score}')
    else:
        score = getattr(metrics, ms.metrics)(y_test, y_pred)
        print(f'{ms.metrics} in testing set: {score}')

'''
import sklearn.metrics as metrics
if cv.scoring == None:
    if esti.is_regr:
        score = metrics.mean_squared_error(y_test, y_pred)
    else:
        score = metrics.r2(y_test, y_pred)
else:
    score = getattr(metrics, 'f1_score')(y_test, y_pred, average='weighted') #None
print(score)
'''
sys.path.insert(1, 'output')
import OutputMgr as omgr
omgr.OutputMgr.cleanOutDir()

esti.output_manager.saveParams(best_estimator['esti'])

sys.path.insert(1, 'output')
import Preprocessing_OM
if 'scale' in best_estimator.named_steps:
    best_scaler = best_estimator['scale']
else:
    best_scaler = None
if 'reduce_dims' in best_estimator.named_steps:
    best_reduce_dims = best_estimator['reduce_dims']
else:
    best_reduce_dims = None
Preprocessing_OM.savePPParams(best_scaler, best_reduce_dims, esti)

if esti.nick == 'knn':
    omgr.OutputMgr.saveTrainingSet(X_train, y_train, esti)


if op != None:
    if op.is_dataset_test:
        if op.dataset_test_size == 1:
            omgr.OutputMgr.saveTestingSet(X_test, y_test, esti)
        elif op.dataset_test_size < 1:
            n_tests = int(y_test * op.dataset_test_size.shape[0])
            omgr.OutputMgr.saveTestingSet(X_test[0:n_tests], y_test[0:n_tests], esti)
        elif op.dataset_test_size != None:
            omgr.OutputMgr.saveTestingSet(X_test[0:op.dataset_test_size].shape[0], y_test[0:op.dataset_test_size].shape[0], esti)
        elif op.dataset_test_size == None:
            omgr.OutputMgr.saveTestingSet(X_test, y_test, esti)

    if op.export_path != None:
        from distutils.dir_util import copy_tree
        omgr.OutputMgr.cleanSIMDirs(f'{op.export_path}/')
        fromDirectory = f"./out/include"
        toDirectory = f"{op.export_path}/dlm/include"
        copy_tree(fromDirectory, toDirectory)
        fromDirectory = f"./out/source"
        toDirectory = f"{op.export_path}/dlm/source"
        copy_tree(fromDirectory, toDirectory)
        fromDirectory = f"./out/model"
        toDirectory = f"{op.export_path}/dlm/model"
        copy_tree(fromDirectory, toDirectory)

print('The end')