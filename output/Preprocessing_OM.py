import numpy as np
from sklearn import preprocessing

from OutputMgr import OutputMgr

# Pre-procssing parameters
def savePPParams(scaler, reduce_dims, estimator):
    #outdir = OutputMgr.checkCreateDSDir(estimator.dataset.name, estimator.nick)
    outdirI = OutputMgr.getOutIncludeDir()

    if scaler == None:
        sx = np.ones(estimator.dataset.X.shape[1])
    else:
        sx = scaler.scale_
        if isinstance(scaler, preprocessing.StandardScaler):
            ux = scaler.mean_
        elif isinstance(scaler, preprocessing.MinMaxScaler):
            mx = scaler.min_

    if reduce_dims == None:
        pca_components = np.identity(estimator.dataset.X.shape[1])
    else:
        pca_components = reduce_dims.components_

    myFile = open(f"{outdirI}PPParams.h","w+")
    myFile.write(f"#ifndef PPPARAMS_H\n")
    myFile.write(f"#define PPPARAMS_H\n\n")

    myFile.write(f"#ifndef PCA_N_FEATURE\n")
    myFile.write(f"#define PCA_N_FEATURE {pca_components.shape[0]}\n")
    myFile.write(f"#endif\n\n")
    myFile.write(f"#ifndef PCA_N_ORIG_FEATURE\n")
    myFile.write(f"#define PCA_N_ORIG_FEATURE {pca_components.shape[1]}\n")
    myFile.write(f"#endif\n\n")
    myFile.write(f"extern float pca_components[PCA_N_FEATURE][PCA_N_ORIG_FEATURE];\n")
    myFile.write(f"\n")

    if scaler!=None:
        if isinstance(scaler, preprocessing.StandardScaler):
            myFile.write(f"#define STANDARD_SCALING\n\n")
            myFile.write(f"extern float s_x[PCA_N_ORIG_FEATURE];\n")
            myFile.write(f"extern float u_x[PCA_N_ORIG_FEATURE];\n")
        elif isinstance(scaler, preprocessing.MinMaxScaler):
            myFile.write(f"#define MINMAX_SCALING\n\n")
            myFile.write(f"extern float s_x[PCA_N_ORIG_FEATURE];\n")
            myFile.write(f"extern float m_x[PCA_N_ORIG_FEATURE];\n")

    '''
    if cfg.normalization!=None and cfg.regr and cfg.algo.lower() != 'dt':
        saveTestNormalization(myFile)
    '''

    myFile.write(f"#endif")
    myFile.close()
    #outdirI = OutputMgr.checkCreateGeneralIncludeDir()
    #from shutil import copyfile
    #copyfile(f"{outdir}PPParams.h", f"{outdirI}PPParams.h")

    outdirS = OutputMgr.getOutSourceDir()
    myFile = open(f"{outdirS}preprocess_params.c","w+")
    myFile.write(f"#include \"PPParams.h\"\n")

    import sys
    sys.path.insert(1, 'utils')
    import create_matrices
    stri = create_matrices.createMatrix('float', 'pca_components', pca_components, 'PCA_N_FEATURE', 'PCA_N_ORIG_FEATURE')
    myFile.write(stri)
    myFile.write(f"\n")

    if scaler!=None:
        if isinstance(scaler, preprocessing.StandardScaler):
            myFile.write(f"#define STANDARD_SCALING\n\n")
            stri = create_matrices.createArray('float', "s_x", np.reshape(sx, (sx.shape[0], )), 'PCA_N_ORIG_FEATURE')
            myFile.write(stri)
            stri = create_matrices.createArray('float', "u_x", np.reshape(ux, (ux.shape[0], )), 'PCA_N_ORIG_FEATURE')
            myFile.write(stri)
        elif isinstance(scaler, preprocessing.MinMaxScaler):
            myFile.write(f"#define MINMAX_SCALING\n\n")
            stri = create_matrices.createArray('float', "s_x", np.reshape(sx, (sx.shape[0], )), 'PCA_N_ORIG_FEATURE')
            myFile.write(stri)
            stri = create_matrices.createArray('float', "m_x", np.reshape(mx, (mx.shape[0], )), 'PCA_N_ORIG_FEATURE')
            myFile.write(stri)
    myFile.close()