import abc
from OutputMgr import OutputMgr

class Knn_OM(OutputMgr):
    def __init__(self, estimator):
        super().__init__()
        self.estimator = estimator

    def saveParams(self, best_estimator):
        #outdir = OutputMgr.checkCreateDSDir(self.estimator.dataset.name, self.estimator.nick)
        outdirI = OutputMgr.getOutIncludeDir()

        k = getattr(best_estimator,'n_neighbors')

        myFile = open(f"{outdirI}KNN_params.h","w+")
        myFile.write(f"#ifndef KNN_PARAMS_H\n")
        myFile.write(f"#define KNN_PARAMS_H\n\n")
        if self.estimator.is_regr == False:
            myFile.write(f"#define N_CLASS {self.estimator.n_classes}\n\n")
        else:
            myFile.write(f"#define N_CLASS 0\n\n")
        myFile.write(f"#define K {k}\n\n")
        myFile.write(f"#endif")
        myFile.close()
        
        #outdirI = OutputMgr.checkCreateGeneralIncludeDir()
        #from shutil import copyfile
        #copyfile(f"{outdir}KNN_params.h", f"{outdirI}KNN_params.h")
