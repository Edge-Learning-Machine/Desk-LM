import argparse
import numpy as np
import os
import joblib as jl
import sys
import sklearn as skl

import logger as lg

class ELM(object):

    predict = None
    dataset = None
    estimator = None
    preprocess = None
    modelselection = None
    output = None

    training_set_cap = None
    args = None

    @staticmethod
    def init(args):

        ELM.args = args
        print("Python version")
        print (sys.version)
        print("Numpy version")
        print(np.__version__) 
        print("Sklearn version")
        print(skl.__version__) 

        sys.path.insert(1, 'config')
        if args.predict != None:
            import Predict as pred
            try:
                ELM.predict = pred.Predict(args.predict)
            except ValueError as err:
                return err
            return 0
        else:
            import Dataset as cds
            try:
                ELM.dataset = cds.Dataset(args.dataset)
            except ValueError as err:
                return err

            import Estimator as ce
            try:
                ELM.estimator = ce.Estimator.create(args.estimator, ELM.dataset)
            except ValueError as err:
                return err

            import Preprocess as pp
            try:
                ELM.preprocess = pp.Preprocess(args.preprocess)
            except ValueError as err:
                return err

            import ModelSelection as ms
            try:
                ELM.modelselection = ms.ModelSelection(args.selection, ELM.estimator)
            except ValueError as err:
                return err

            if args.output != None:
                import Output
                try:
                    ELM.output = Output.Output(args.output)
                except ValueError as err:
                    return err
                if ELM.estimator.nick=='knn':
                    ELM.training_set_cap = ELM.output.training_set_cap
            return 0

    @staticmethod
    def process():
        if ELM.predict != None:
            m = jl.load(os.path.join('storage/', ELM.predict.model_id + '.pkl'))
            p = m.predict(ELM.predict.samples)
            print(p)
        else:
            from sklearn.model_selection import train_test_split
            X_train, X_test, y_train, y_test = train_test_split(
                ELM.dataset.X, ELM.dataset.y, train_size=ELM.training_set_cap, test_size=ELM.dataset.test_size, random_state=0)

            col_means = X_train.mean()
            X_train = X_train.fillna(col_means)
            X_test = X_test.fillna(col_means)

            best_estimator = ELM.estimator.process(ELM.preprocess, ELM.modelselection, X_train, y_train)
            #print(best_estimator.score(X_test, y_test))
            y_pred = best_estimator.predict(X_test)

            import sklearn.metrics as metrics
            if hasattr(ELM.modelselection, 'metrics_average'):
                score = getattr(metrics, ELM.modelselection.metrics)(y_test, y_pred, average=ELM.modelselection.metrics_average)
                print(f'{ELM.modelselection.metrics}, average={ELM.modelselection.metrics_average} in testing set: {score}')
            else:
                if hasattr(ELM.modelselection, 'is_RMSE'):
                    score = getattr(metrics, ELM.modelselection.metrics)(y_test, y_pred, squared=not ELM.modelselection.is_RMSE)
                    pref = ''
                    if ELM.modelselection.is_RMSE:
                        pref='root_'
                    print(f'{pref}{ELM.modelselection.metrics} in testing set: {score}')
                else:
                    score = getattr(metrics, ELM.modelselection.metrics)(y_test, y_pred)
                    print(f'{ELM.modelselection.metrics} in testing set: {score}')

            if ELM.args.store == True:
                import uuid
                uuid_str = str(uuid.uuid4())
                jl.dump(best_estimator, './storage/' + uuid_str + '.pkl', compress = 3)
                print('Stored model: ' + uuid_str)

            if ELM.args.output != None:
                sys.path.insert(1, 'output')
                import OutputMgr as omgr
                omgr.OutputMgr.cleanOutDir()

                ELM.estimator.output_manager.saveParams(best_estimator['esti'])

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
                Preprocessing_OM.savePPParams(best_scaler, best_reduce_dims, ELM.estimator)

                if ELM.estimator.nick == 'knn':
                    omgr.OutputMgr.saveTrainingSet(X_train, y_train, ELM.estimator)

                if ELM.output != None:
                    if ELM.output.is_dataset_test:
                        if ELM.output.dataset_test_size == 1:
                            omgr.OutputMgr.saveTestingSet(X_test, y_test, ELM.estimator)
                        elif ELM.output.dataset_test_size < 1:
                            n_tests = int(y_test * ELM.output.dataset_test_size.shape[0])
                            omgr.OutputMgr.saveTestingSet(X_test[0:n_tests], y_test[0:n_tests], ELM.estimator)
                        elif ELM.output.dataset_test_size != None:
                            omgr.OutputMgr.saveTestingSet(X_test[0:ELM.output.dataset_test_size].shape[0], y_test[0:ELM.output.dataset_test_size].shape[0], ELM.estimator)
                        elif ELM.output.dataset_test_size == None:
                            omgr.OutputMgr.saveTestingSet(X_test, y_test, ELM.estimator)

                    if ELM.output.export_path != None:
                        from distutils.dir_util import copy_tree
                        omgr.OutputMgr.cleanSIMDirs(f'{ELM.output.export_path}/')
                        fromDirectory = f"./out/include"
                        toDirectory = f"{ELM.output.export_path}/dlm/include"
                        copy_tree(fromDirectory, toDirectory)
                        fromDirectory = f"./out/source"
                        toDirectory = f"{ELM.output.export_path}/dlm/source"
                        copy_tree(fromDirectory, toDirectory)
                        fromDirectory = f"./out/model"
                        toDirectory = f"{ELM.output.export_path}/dlm/model"
                        copy_tree(fromDirectory, toDirectory)
        print('The end')


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
    
    res = ELM.init(args)
    if  res == 0:
        ELM.process()
    else:
        print(res)