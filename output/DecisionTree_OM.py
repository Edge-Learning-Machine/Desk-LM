import abc
from OutputMgr import OutputMgr
import numpy as np

class DecisionTree_OM(OutputMgr):
    def __init__(self, estimator):
        super().__init__()
        self.estimator = estimator

    def saveParams(self, best_estimator):
        # outdir = OutputMgr.checkCreateDSDir(self.estimator.dataset.name, self.estimator.nick)
        outdirI = OutputMgr.getOutIncludeDir()

        n_nodes = getattr(best_estimator.tree_,'node_count')
        values = getattr(best_estimator.tree_,'value')
        children_left = getattr(best_estimator.tree_,'children_left')
        children_right = getattr(best_estimator.tree_,'children_right')
        feature = getattr(best_estimator.tree_,'feature')
        threshold = getattr(best_estimator.tree_,'threshold')
        target_classes = np.unique(self.estimator.dataset.y)

        myFile = open(f"{outdirI}DT_params.h","w+")
        myFile.write(f"#ifndef DT_PARAMS_H\n")
        myFile.write(f"#define DT_PARAMS_H\n\n")
        if self.estimator.is_regr == False:
            myFile.write(f"#define N_CLASS {self.estimator.n_classes}\n")
            leaf_nodes = children_left == children_right
            n_leaves = np.count_nonzero(leaf_nodes)
            myFile.write(f"#define N_LEAVES {n_leaves}\n\n")
        else:
            myFile.write(f"#define N_CLASS 0\n\n")
        myFile.write(f"#define VALUES_DIM {values.shape[2]}\n\n")
        myFile.write(f"#define N_NODES {n_nodes}\n\n")

        myFile.write(f"extern int children_left[N_NODES];\n")
        myFile.write(f"extern int children_right[N_NODES];\n")
        myFile.write(f"extern int feature[N_NODES];\n")
        myFile.write(f"extern float threshold[N_NODES];\n")
        if self.estimator.is_regr == True:
            myFile.write(f"extern int values[N_NODES][VALUES_DIM];\n")
        else:
            myFile.write(f"extern int target_classes[N_CLASS];\n")
            myFile.write(f"extern int leaf_nodes[N_LEAVES][2+VALUES_DIM];\n")
        myFile.write(f"\n#endif")
        myFile.close()

        #outdirI = OutputMgr.checkCreateGeneralIncludeDir()
        #from shutil import copyfile
        #copyfile(f"{outdir}DT_params.h", f"{outdirI}DT_params.h")

        outdirS = OutputMgr.getOutSourceDir()
        myFile = open(f"{outdirS}DT_params.c","w+")
        myFile.write(f"#include \"DT_params.h\"\n")

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
        if self.estimator.is_regr == True:
            stri = create_matrices.createMatrix2('int', 'values', values, 'N_NODES', 'VALUES_DIM') 
            myFile.write(stri)
        else:
            stri = create_matrices.createArray("int", "target_classes", target_classes, 'N_CLASS')
            myFile.write(stri)
            argmaxs = np.argmax(values[leaf_nodes][:,0], axis=1).reshape(-1,1)
            leaf_nodes_idx = np.asarray(np.nonzero(leaf_nodes)).T
            leaf_node_mat = np.concatenate((leaf_nodes_idx, argmaxs), axis=1)
            leaf_node_values = values[leaf_nodes][:,0].reshape(n_leaves, -1)
            leaf_node_mat = np.concatenate((leaf_node_mat, leaf_node_values), axis=1)
            stri = create_matrices.createMatrix('int', 'leaf_nodes', leaf_node_mat, 'N_LEAVES', '2+VALUES_DIM') 
            myFile.write(stri)
        myFile.close()