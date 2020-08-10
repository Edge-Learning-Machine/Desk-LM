import abc
from OutputMgr import OutputMgr
import numpy as np

class TripleES_OM(OutputMgr):
    def __init__(self, tripleES):
        super().__init__()
        self.tripleES = tripleES


    def saveParams(self, best_estimator):
        outdirI = OutputMgr.getOutIncludeDir()

        alpha = best_estimator.alpha
        beta = best_estimator.beta
        gamma = best_estimator.gamma
        scaling_factor = best_estimator.scaling_factor
        season_length = best_estimator.season_length

    #apro il file .h con i paramatetri alpha, beta, gamma trovati facendo la cv
        myFile = open(f"{outdirI}TripleES_params.h","w+")
        myFile.write(f"#ifndef TripleES_PARAMS_H\n")
        myFile.write(f"#define TripleES_PARAMS_H\n\n")
        myFile.write(f"#define ALPHA {alpha}\n")
        myFile.write(f"#define BETA {beta}\n")
        myFile.write(f"#define GAMMA {gamma}\n")
        myFile.write(f"#define SCALING_FACTOR {scaling_factor}\n")
        myFile.write(f"#define SEASON_LENGTH {season_length}\n")
        myFile.write(f"\n#endif")
        myFile.close()
