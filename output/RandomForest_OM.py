import abc
from OutputMgr import OutputMgr
import numpy as np

def unrollPointers(name, lenght):
		if lenght == 1:
			stri = "{" + f" &{name}_t1" + "}"
		else:
			stri = "{ "
			for i in range(lenght-1):
				stri = stri + f"&{name}_t{i} ,"
			stri = stri + f"&{name}_t{lenght-1}"
			stri = stri + "};"
		return stri

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
			
		for i, t in enumerate(rf):
			n_nodes = getattr(t.tree_,'node_count')
			values = getattr(t.tree_,'value')
			
			myFile.write(f"/// VARIABLES FOR TREE NUMBER {i} \n\n")
			myFile.write(f"#define N_NODES_t{i} {n_nodes}\n\n")
			myFile.write(f"#define VALUES_DIM_t{i} {values.shape[2]}\n\n")

			myFile.write(f"extern int children_left_t{i}[N_NODES_t{i}];\n")
			myFile.write(f"extern int children_right_t{i}[N_NODES_t{i}];\n")
			myFile.write(f"extern int feature_t{i}[N_NODES_t{i}];\n")
			myFile.write(f"extern float threshold_t{i}[N_NODES_t{i}];\n")
			myFile.write(f"extern int values_t{i}[N_NODES_t{i}][VALUES_DIM_t{i}];\n")
			myFile.write(f"\n\n")
		
		myFile.write(f"/// Arrays for the whole forest to make it easier to use \n\n")
		myFile.write(f"extern int* forest_children_left[FOREST_DIM];\n")
		myFile.write(f"extern int* forest_children_right[FOREST_DIM];\n")
		myFile.write(f"extern int* forest_feature[FOREST_DIM];\n")
		myFile.write(f"extern float* forest_threshold[FOREST_DIM];\n")
		myFile.write(f"extern int** forest_values[FOREST_DIM];\n")
			
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
		
		for i,t in enumerate(rf):
			
			values = getattr(t.tree_,'value')
			children_left = getattr(t.tree_,'children_left')
			children_right = getattr(t.tree_,'children_right')
			feature = getattr(t.tree_,'feature')
			threshold = getattr(t.tree_,'threshold')
			target_classes = np.unique(self.estimator.dataset.y)
			
			
			stri = create_matrices.createArray("int", f"children_left_t{i}", children_left, f'N_NODES_t{i}')
			myFile.write(stri)
			stri = create_matrices.createArray("int", f"children_right_t{i}", children_right, f'N_NODES_t{i}')
			myFile.write(stri)
			stri = create_matrices.createArray("int", f"feature_t{i}", feature, f'N_NODES_t{i}')
			myFile.write(stri)
			stri = create_matrices.createArray("float", f"threshold_t{i}", threshold, f'N_NODES_t{i}')
			myFile.write(stri)
			stri = create_matrices.createMatrix2('int', f'values_t{i}', values, f'N_NODES_t{i}', f'VALUES_DIM_t{i}') 
			myFile.write(stri)
			
		
		if self.estimator.is_regr == False:
			stri = create_matrices.createArray("int", "target_classes", target_classes, 'N_CLASS')
			myFile.write(stri)
			
			
		
		stri = unrollPointers("children_left", len(rf))
		myFile.write(f"forest_children_left= {stri}\n")
		
		stri = unrollPointers("children_right", len(rf))
		myFile.write(f"forest_children_right = {stri}\n")
		
		stri = unrollPointers("feature", len(rf))
		myFile.write(f"forest_feature = {stri}\n")
		
		stri = unrollPointers("threshold", len(rf))
		myFile.write(f"forest_threshold = {stri}\n")
		
		stri = unrollPointers("values", len(rf))
		myFile.write(f"forest_values = {stri}\n")
		
		myFile.close()
		
