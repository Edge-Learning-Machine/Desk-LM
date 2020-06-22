import abc
from OutputMgr import OutputMgr

import numpy as np

class SVM_OM(OutputMgr):
    def __init__(self, estimator):
        super().__init__()
        self.estimator = estimator

    def saveParams(self, best_estimator):
        #outdir = OutputMgr.checkCreateDSDir(self.estimator.dataset.name, self.estimator.nick)
        outdirI = OutputMgr.getOutIncludeDir()

        myFile = open(f"{outdirI}SVM_params.h","w+")
        myFile.write(f"#ifndef SVM_PARAMS_H\n")
        myFile.write(f"#define SVM_PARAMS_H\n\n")
        if self.estimator.is_regr == False:
            myFile.write(f"#define N_CLASS {self.estimator.n_classes}\n\n")
            myFile.write(f"#define WEIGTH_DIM {best_estimator.coef_.shape[0]}\n\n")
            myFile.write(f"#ifndef N_FEATURE\n")
            myFile.write(f"#define N_FEATURE {best_estimator.coef_.shape[1]}\n")
            myFile.write(f"#endif\n\n")
        else:
            myFile.write(f"#define N_CLASS 0\n\n")
            myFile.write(f"#define WEIGTH_DIM 1\n\n")
            myFile.write(f"#ifndef N_FEATURE\n")
            myFile.write(f"#define N_FEATURE {best_estimator.coef_.shape[1]}\n")
            myFile.write(f"#endif\n\n")

        if self.estimator.is_regr == False:
            myFile.write(f"extern float support_vectors[WEIGTH_DIM][N_FEATURE];\n")
        else: #Same as above as a declaration
            myFile.write(f"extern float support_vectors[WEIGTH_DIM][N_FEATURE];\n")
        
        myFile.write(f"extern float bias[WEIGTH_DIM];\n")
        myFile.write(f"\n#endif")
        myFile.close()
        
        outdirS = OutputMgr.getOutSourceDir()
        myFile = open(f"{outdirS}SVM_params.c","w+")
        myFile.write(f"#include \"SVM_params.h\"\n")

        import sys
        sys.path.insert(1, 'utils')
        import create_matrices
        if self.estimator.is_regr == False:
            stri = create_matrices.createMatrix('float', 'support_vectors', best_estimator.coef_, 'WEIGTH_DIM', 'N_FEATURE')
        else:
            stri = create_matrices.createMatrix("float", "support_vectors", np.reshape(best_estimator.coef_, (1, best_estimator.coef_.shape[1])), 'WEIGTH_DIM', 'N_FEATURE')   
        myFile.write(stri)
        stri = create_matrices.createArray("float", "bias", best_estimator.intercept_, 'WEIGTH_DIM')
        myFile.write(stri)
        myFile.close()
