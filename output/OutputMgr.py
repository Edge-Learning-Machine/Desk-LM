import abc

import os

import error as error

class OutputMgr(metaclass=abc.ABCMeta):
   
    @abc.abstractmethod
    def saveParams(self, estimator):
        """Save data to the output."""
    '''   
    def checkCreateDSDir(ds_name, algo_name):
        outdir = './out/'
        if os.path.isdir(outdir) == False:
            os.mkdir(outdir)
        outdir = './out/' + ds_name
        if os.path.isdir(outdir) == False:
            os.mkdir(outdir)
        outdir = './out/' + ds_name + '/include/'
        if os.path.isdir(outdir) == False:
            os.mkdir(outdir)
        outdir = './out/' + ds_name + '/include/' + algo_name + '/'
        if os.path.isdir(outdir) == False:
            os.mkdir(outdir)
        return outdir
  
    def checkCreateGeneralIncludeDir():
        outdir = './out/'
        if os.path.isdir(outdir) == False:
            os.mkdir(outdir)
        outdir = './out/include/'
        if os.path.isdir(outdir) == False:
            os.mkdir(outdir)
        return outdir

    def checkCreateGeneralSourceDir():
        outdir = './out/'
        if os.path.isdir(outdir) == False:
            os.mkdir(outdir)
        outdir = './out/source/'
        if os.path.isdir(outdir) == False:
            os.mkdir(outdir)
        return outdir
  '''

    def getOutIncludeDir():
        outdir = './out/include/'
        return outdir

    def getOutSourceDir():
        outdir = './out/source/'
        return outdir

    def getOutModelDir():
        outdir = './out/model/'
        return outdir

    def cleanSIMDirs(path):
        import shutil
        try:
            if (os.path.exists(path+'/ds/source/')):
                shutil.rmtree(path+'/ds/source/', ignore_errors=True)
            if (os.path.exists(path+'/ds/include/')):
                shutil.rmtree(path+'/ds/include/', ignore_errors=True)
            if (os.path.exists(path+'/ds/model/')):
                shutil.rmtree(path+'/ds/model/', ignore_errors=True)
            if os.path.isdir(path) == False:
                os.mkdir(path)
            if os.path.isdir(path+'/ds') == False:
                os.mkdir(path+'/ds')
            os.mkdir(path+'/ds/source/')
            os.mkdir(path+'/ds/include/')
            os.mkdir(path+'/ds/model/')
        except PermissionError as err:
            print(err)
            print(error.errors['output_permission'])


    def cleanOutDir():
        import shutil
        try:
            if (os.path.exists('./out/source/')):
                shutil.rmtree('./out/source/', ignore_errors=True)
            if (os.path.exists('./out/include/')):
                shutil.rmtree('./out/include/', ignore_errors=True)
            if (os.path.exists('./out/model/')):
                shutil.rmtree('./out/model/', ignore_errors=True)
            if os.path.isdir('./out') == False:
                os.mkdir('./out')
            os.mkdir('./out/source/')
            os.mkdir('./out/include/')
            os.mkdir('./out/model/')
            '''
            if (os.path.exists('./out/source/')):
                shutil.rmtree('./out/source/', ignore_errors=True)
            if os.path.isdir('./out') == False:
                os.mkdir('./out')
            if os.path.isdir('./out/source/') == False:
                os.mkdir('./out/source')
            shutil.rmtree('./out/include/', ignore_errors=True)
            os.mkdir('./out/include/')
            '''
        except PermissionError as err:
            print(err)
            print(error.errors['output_permission'])

    def saveTestingSet(X_test, y_test, estimator):
        import pandas as pd
        if isinstance(X_test, pd.core.series.Series):
                X_test = X_test.to_frame()
        #outdir = OutputMgr.checkCreateDSDir(estimator.dataset.name, estimator.nick)
        outdirI = OutputMgr.getOutIncludeDir()

        myFile = open(f"{outdirI}testing_set.h","w+")
        myFile.write(f"#ifndef TESTINGSET_H\n")
        myFile.write(f"#define TESTINGSET_H\n\n")

        myFile.write(f"#define N_TEST {y_test.shape[0]}\n\n")
        myFile.write(f"#ifndef N_FEATURE\n")
        myFile.write(f"#define N_FEATURE {X_test.shape[1]}\n")
        myFile.write(f"#endif\n\n")
        myFile.write(f"#ifndef N_ORIG_FEATURE\n")
        myFile.write(f"#define N_ORIG_FEATURE {X_test.shape[1]}\n") # Is this value correct??? xxx
        myFile.write(f"#endif\n\n")
        if estimator.is_regr:
            type_s = 'float'
        else:
            type_s = 'int'
        myFile.write(f"extern {type_s} y_test[N_TEST];\n")
        myFile.write(f"extern float X_test[N_TEST][N_FEATURE];\n")
        
        #
        #if cfg.normalization!=None and cfg.regr and cfg.algo.lower() != 'dt':
        #    saveTestNormalization(myFile)
        #
        
        myFile.write(f"#endif")
        myFile.close()
        #outdirI = OutputMgr.checkCreateGeneralIncludeDir()
        #from shutil import copyfile
        #copyfile(f"{outdir}testing_set.h", f"{outdirI}testing_set.h")

        outdirS = OutputMgr.getOutSourceDir()
        myFile = open(f"{outdirS}testing_set.c","w+")

        myFile.write(f"#include \"testing_set.h\"\n")

        if estimator.is_regr:
            type_s = 'float'
        else:
            type_s = 'int'
        import sys
        sys.path.insert(1, 'utils')
        import create_matrices
        import numpy as np
        stri = create_matrices.createArray(type_s, "y_test", np.reshape(y_test, (y_test.shape[0], )), 'N_TEST')
        myFile.write(stri)
        
        stri = create_matrices.createMatrix('float', 'X_test', X_test.values, 'N_TEST', 'N_FEATURE') # changed by FB
        myFile.write(stri)
        myFile.close()

    def saveTrainingSet(X_train, y_train, estimator):
        #outdir = OutputMgr.checkCreateDSDir(estimator.dataset.name, estimator.nick)
        outdirI = OutputMgr.getOutIncludeDir()

        myFile = open(f"{outdirI}training_set.h","w+")
        myFile.write(f"#define N_TRAIN {y_train.shape[0]}\n\n")
        myFile.write(f"#ifndef N_FEATURE\n")
        myFile.write(f"#define N_FEATURE {X_train.shape[1]}\n")
        myFile.write(f"#endif\n\n")

        if estimator.is_regr:
            type_s = 'float'
        else:
            type_s = 'int'
        myFile.write(f"extern {type_s} y_train[N_TRAIN];\n")
        myFile.write(f"extern float X_train[N_TRAIN][N_FEATURE];\n")
        myFile.close()
        
        #outdirI = OutputMgr.checkCreateGeneralIncludeDir()
        #from shutil import copyfile
        #copyfile(f"{outdir}training_set.h", f"{outdirI}training_set.h")

        outdirS = OutputMgr.getOutSourceDir()
        myFile = open(f"{outdirS}training_set_params.c","w+")
        #myFile.write(f"#include \"AI_main.h\"\n")
        myFile.write(f"#include \"training_set.h\"\n")

        if estimator.is_regr:
            type_s = 'float'
        else:
            type_s = 'int'
        import sys
        sys.path.insert(1, 'utils')
        import create_matrices
        import numpy as np
        stri = create_matrices.createArray(type_s, "y_train", np.reshape(y_train, (y_train.shape[0], )), 'N_TRAIN')
        myFile.write(stri)
        stri = create_matrices.createMatrix('float', 'X_train', X_train.values, 'N_TRAIN', 'N_FEATURE') # changed by FB
        myFile.write(stri)
        myFile.close()