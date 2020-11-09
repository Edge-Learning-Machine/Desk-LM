import abc
from OutputMgr import OutputMgr
import numpy as np

class RandomForest_OM(OutputMgr):
    def __init__(self, estimator):
        super().__init__()
        self.estimator = estimator

    def saveParams(self, best_estimator):
        # outdir = OutputMgr.checkCreateDSDir(self.estimator.dataset.name, self.estimator.nick)
        outdirI = OutputMgr.getOutIncludeDir()

		rf = best_estimator.estimators_
		


        myFile = open(f"{outdirI}RF_params.h","w+")
        myFile.write(f"#ifndef RF_PARAMS_H\n")
        myFile.write(f"#define RF_PARAMS_H\n\n")
		
		myFile.write(f"#define FOREST_DIM {len(rf)}\n\n")
		
        if self.estimator.is_regr == False:
            myFile.write(f"#define N_CLASS {self.estimator.n_classes}\n\n")
        else:
            myFile.write(f"#define N_CLASS 0\n\n")
			
		myFile.write(f"/// define the number of nodes for each tree in the forest\n\n")
		
		for i, t in enumerate(rf):
			n_nodes = getattr(t.tree_,'node_count')		
			myFile.write(f"#define N_NODES_TREE_{i} {n_nodes}\n\n")
		
		myFile.write(f"#define VALUES_DIM {values.shape[2]}\n\n")
		
		myFile.write(f"/// tree struct definition\n\n")
		myFile.write(f"typedef struct MyTree {\n")
		myFile.write(f"int children_left[];\n")
		myFile.write(f"int children_right[];\n")
		myFile.write(f"int feature[];\n")
		myFile.write(f"float threshold[];\n")
		myFile.write(f"int values[][];\n")
		myFile.write(f"int feature[];\n")
		if self.estimator.is_regr == False:
			myFile.write(f"int target_classes[N_CLASS];\n")
		myFile.write(f"} MyTree;\n\n\n")
        
		myFile.write(f"extern MyTree forest[FOREST_DIM];\n")
        
        myFile.write(f"\n#endif")
        myFile.close()

        #outdirI = OutputMgr.checkCreateGeneralIncludeDir()
        #from shutil import copyfile
        #copyfile(f"{outdir}DT_params.h", f"{outdirI}DT_params.h")

        outdirS = OutputMgr.getOutSourceDir()
        myFile = open(f"{outdirS}RF_params.c","w+")
        myFile.write(f"#include \"RF_params.h\"\n")

        import sys
        sys.path.insert(1, 'utils')
        import create_matrices
        stri = create_matrices.createArray("int", "children_left", children_left, 'N_NODES')
        myFile.write(stri)
        stri = create_matrices.createArray("int", "children_right", children_right, 'N_NODES')
        myFile.write(stri)
        stri = create_matrices.createArray("int", "feature", feature, 'N_NODES')
        myFile.write(stri)
        stri = create_matrices.createArray("float", "threshold", threshold, 'N_NODES')
        myFile.write(stri)
        stri = create_matrices.createMatrix2('int', 'values', values, 'N_NODES', 'VALUES_DIM') 
        myFile.write(stri)
        if self.estimator.is_regr == False:
            stri = create_matrices.createArray("int", "target_classes", target_classes, 'N_CLASS')
            myFile.write(stri)
        myFile.close()