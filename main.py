import argparse
import numpy as np
import os
import joblib as jl
import sys
import sklearn as skl
import logger as lg
import error as error
import uuid


class ELM(object):

    def __init__(self, args):
        self.args = args
        self.predict = None
        self.dataset = None
        self.estimator = None
        self.preprocess = None
        self.modelselection = None
        self.output = None
        self.training_set_cap = None

        print("Python version")
        print (sys.version)
        print("Numpy version")
        print(np.__version__) 
        print("Sklearn version")
        print(skl.__version__) 
        
        sys.path.insert(1, 'config')
        if self.args.predict != None:
            import Predict as pred
            try:
                self.predict = pred.Predict(self.args.predict)
            except ValueError as err:
                raise ValueError(err)
        else:
            import Dataset as cds
            try:
                if isinstance(self.args.dataset, str):
                    self.dataset = cds.Dataset(self.args.dataset)
                else:
                    self.dataset = cds.Dataset(self.args.dataset, self.args.columns, self.args.target)
            except ValueError as err:
                raise ValueError(err)

            import Estimator as ce
            try:
                self.estimator = ce.Estimator.create(self.args.estimator, self.dataset)
            except ValueError as err:
                raise ValueError(err)

            import Preprocess as pp
            try:
                self.preprocess = pp.Preprocess(self.args.preprocess)
            except ValueError as err:
                raise ValueError(err)

            import ModelSelection as ms
            try:
                self.modelselection = ms.ModelSelection(self.args.selection, self.estimator)
            except ValueError as err:
                raise ValueError(err)

            if self.args.output != None:
                import Output
                try:
                    self.output = Output.Output(self.args.output)
                except ValueError as err:
                    raise ValueError(err)
                if self.estimator.nick=='knn':
                    self.training_set_cap = self.output.training_set_cap

    def process(self, **kargs):
        if self.predict != None:
            m = jl.load(os.path.join('storage/', self.predict.model_id + '.pkl'))
            from TripleES import TripleES
            if isinstance(m, TripleES):
                if not hasattr(self.predict, 'n_preds'):
                    raise ValueError(error.errors['miss_n_preds'])
                predicted = m.predict_from_series(self.predict.samples, self.predict.n_preds)
            else:
                predicted = m.predict(self.predict.samples)
            print(f'Predicted values: {predicted}')
            results = predicted
        else:
            from sklearn.model_selection import train_test_split
            shuffle = True
            if self.estimator.nick == 'TripleES':
                shuffle = False
            X_train, X_test, y_train, y_test = train_test_split(
                self.dataset.X, self.dataset.y, train_size=self.training_set_cap, test_size=self.dataset.test_size, shuffle = shuffle)

            col_means = X_train.mean()
            X_train = X_train.fillna(col_means)
            X_test = X_test.fillna(col_means)

            best_estimator = self.estimator.process(self.preprocess, self.modelselection, X_train, y_train)
            #print(best_estimator.score(X_test, y_test))
            y_pred = best_estimator.predict(X_test)

            import sklearn.metrics as metrics
            if hasattr(self.modelselection, 'metrics_average'):
                score = getattr(metrics, self.modelselection.metrics)(y_test, y_pred, average=self.modelselection.metrics_average)
                print(f'{self.modelselection.metrics}, average={self.modelselection.metrics_average} in testing set: {score}')
                results = (self.modelselection.metrics, self.modelselection.metrics_average, score)
            else:
                if hasattr(self.modelselection, 'is_RMSE'):
                    score = getattr(metrics, self.modelselection.metrics)(y_test, y_pred, squared=not self.modelselection.is_RMSE)
                    pref = ''
                    if self.modelselection.is_RMSE:
                        pref='root_'
                    print(f'{pref}{self.modelselection.metrics} in testing set: {score}')
                else:
                    score = getattr(metrics, self.modelselection.metrics)(y_test, y_pred)
                    print(f'{self.modelselection.metrics} in testing set: {score}')
                #Add/change directly above if you want a different metrics (e.g., r2_score)
                results = (self.modelselection.metrics, score)

            if self.args.store == True:
                model_id = kargs['model_id'] if 'model_id' in kargs  else str(uuid.uuid4())
                jl.dump(best_estimator, './storage/' + model_id + '.pkl', compress = 3)
                print(f'Stored model: {model_id}')

            if self.args.output != None:
                sys.path.insert(1, 'output')
                import OutputMgr as omgr
                omgr.OutputMgr.cleanOutDir()

                if self.estimator.nick == 'TripleES':
                    self.estimator.output_manager.saveParams(best_estimator)
                else:
                    self.estimator.output_manager.saveParams(best_estimator['esti'])

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
                    Preprocessing_OM.savePPParams(best_scaler, best_reduce_dims, self.estimator)

                    if self.estimator.nick == 'knn':
                        omgr.OutputMgr.saveTrainingSet(X_train, y_train, self.estimator)

                if self.output != None:
                    if self.output.is_dataset_test:
                        if self.output.dataset_test_size == 1:
                            omgr.OutputMgr.saveTestingSet(X_test, y_test, self.estimator)
                        elif self.output.dataset_test_size < 1:
                            n_tests = int((y_test * self.output.dataset_test_size).shape[0])
                            omgr.OutputMgr.saveTestingSet(X_test[0:n_tests], y_test[0:n_tests], self.estimator)
                        elif self.output.dataset_test_size != None:
                            omgr.OutputMgr.saveTestingSet(X_test[0:self.output.dataset_test_size].shape[0], y_test[0:self.output.dataset_test_size].shape[0], self.estimator)
                        elif self.output.dataset_test_size == None:
                            omgr.OutputMgr.saveTestingSet(X_test, y_test, self.estimator)

                    if self.output.export_path != None:
                        from distutils.dir_util import copy_tree
                        omgr.OutputMgr.cleanSIMDirs(f'{self.output.export_path}/')
                        fromDirectory = f"./out/include"
                        toDirectory = f"{self.output.export_path}/dlm/include"
                        copy_tree(fromDirectory, toDirectory)
                        fromDirectory = f"./out/source"
                        toDirectory = f"{self.output.export_path}/dlm/source"
                        copy_tree(fromDirectory, toDirectory)
                        fromDirectory = f"./out/model"
                        toDirectory = f"{self.output.export_path}/dlm/model"
                        copy_tree(fromDirectory, toDirectory)
        print('The end')
        return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dataset')
    parser.add_argument('-p', '--preprocess')
    parser.add_argument('-e', '--estimator')
    parser.add_argument('-s', '--selection')
    parser.add_argument('-o', '--output')
    parser.add_argument('--predict')
    parser.add_argument('--store', action="store_true")
    args = parser.parse_args()
    
    try:
        elm = ELM(args)
        elm.process()
    except ValueError as error:
        print(error)