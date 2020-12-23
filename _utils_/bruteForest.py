'''
This script could be used to estimate the best parameters for a random forest (max depth and the number of trees).
It use a brute force approach, so it could require a really long time to return you the data.

Tree variables can be set in this script (search #config) to configure the max number of trees, the limit depth and the number of iteration for each couple of parameters.
Those vars are: maxTrees, maxDepth, maxIter.

This script will return you (for each iteration on each couple) those values: accuracy, .c size, .h size in a complete csv file.

IMPORTANT: just remember that max depth = 0 is actually a limitless depth!

Usage: the usage is pretty similiar to the main script, but the estimator json MUST be input\est_rf_c_brute.json 
It will be overwritten each iteration and it will not be restored when the script ends.

bruteforest.py -d <dataset_config_file> -e input\est_rf_c_brute.json -p <preprocessing_config_file> -s <model_selection_config_file>




'''

import argparse
import numpy as np
import os
import joblib as jl
import sys
import sklearn as skl
import logger as lg
import error as error
import matplotlib.pyplot as plt
from matplotlib import pyplot
from mpl_toolkits.mplot3d import Axes3D


trees_arr = []
mDepth_arr = []
rate_arr = []
hDim_arr = []
cDim_arr = []

tempRate = 0
tempHDim = 0 
tempCDim = 0

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


		
                
		sys.path.insert(1, 'config')
		if self.args.predict != None:
			import Predict as pred
			try:
				self.predict = pred.Predict(self.args.predict)
			except ValueError as err:
                # return err
				raise ValueError(err)
            # return 0
		else:
			import Dataset as cds
			try:
				self.dataset = cds.Dataset(self.args.dataset)
			except ValueError as err:
                # return err
				raise ValueError(err)

			import Estimator as ce
			try:
				self.estimator = ce.Estimator.create(self.args.estimator, self.dataset)
			except ValueError as err:
                # return err
				raise ValueError(err)

			import Preprocess as pp
			try:
				self.preprocess = pp.Preprocess(self.args.preprocess)
			except ValueError as err:
                # return err
				raise ValueError(err)

			import ModelSelection as ms
			try:
				self.modelselection = ms.ModelSelection(self.args.selection, self.estimator)
			except ValueError as err:
                # return err
				raise ValueError(err)

			if self.args.output != None:
				import Output
				try:
					self.output = Output.Output(self.args.output)
				except ValueError as err:
                    # return err
					raise ValueError(err)
				if self.estimator.nick=='knn':
					self.training_set_cap = self.output.training_set_cap
            # return 0

	def process(self, model_id=None):
		if self.predict != None:
			m = jl.load(os.path.join('storage/', self.predict.model_id + '.pkl'))
			from TripleES import TripleES
			if isinstance(m, TripleES):
				if not hasattr(self.predict, 'n_preds'):
					raise ValueError(error.errors['miss_n_preds'])
				p = m.predict_from_series(self.predict.samples, self.predict.n_preds)
			else:
				p = m.predict(self.predict.samples)
			print(f'Predicted values: {p}')
			return p
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
			
			st = open("statsFile.csv", "a")
			global tempRate
			
			if hasattr(self.modelselection, 'metrics_average'):
				score = getattr(metrics, self.modelselection.metrics)(y_test, y_pred, average=self.modelselection.metrics_average)
				tempRate += score
				st.write(f'{score},')
			else:
				if hasattr(self.modelselection, 'is_RMSE'):
					score = getattr(metrics, self.modelselection.metrics)(y_test, y_pred, squared=not self.modelselection.is_RMSE)
					pref = ''
					if self.modelselection.is_RMSE:
						pref='root_'
					tempRate += score
					st.write(f'{score},')
				else:
					score = getattr(metrics, self.modelselection.metrics)(y_test, y_pred)
					
					tempRate += score
					st.write(f'{score},')
                #Add/change directly above if you want a different metrics (e.g., r2_score)

			st.close()

			if self.args.store == True:
				if not model_id:
					import uuid
					model_id = str(uuid.uuid4())
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
							n_tests = int(y_test * self.output.dataset_test_size.shape[0])
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


def buildJson (est,depth):

	
	f = open("input\\est_rf_c_brute.json", "w")
	f.write('{\n')
	f.write('    "estimator": "RandomForestClassifier",\n')
	f.write(f'	"n_estimators": {est} ')
	if depth != 0:
		f.write(f',\n	"max_depth": {depth} \n')
	f.write('}')
	f.close()

if __name__ == '__main__':

	#config
	maxTrees = 21
	maxDepth = 51
	maxIter = 10
	
	parser = argparse.ArgumentParser()
	parser.add_argument('-d', '--dataset')
	parser.add_argument('-p', '--preprocess')
	parser.add_argument('-e', '--estimator')
	parser.add_argument('-s', '--selection')
	parser.add_argument('-o', '--output')
	parser.add_argument('--predict')
	parser.add_argument('--store', action="store_true")
	args = parser.parse_args()
    
	st = open("statsFile.csv", "w")
	st.write('#trees, Max_Depth, #Iteration, rate, .H_Dim, .C_Dim\n')
	st.close()
	
	print(f'Bruteforce to get stats about number of estimators and max depth')
	for x in range(2,maxTrees):
		for y in range(0,maxDepth):
			buildJson(x,y)
			for z in range(0,maxIter):
			
			
			
				print(f'Current: number {x}/{maxTrees}, depth {y}/{maxDepth}, iteration {z}/{maxIter}')
				st = open("statsFile.csv", "a")
				st.write(f'{x}, {y}, {z},')
				st.close()
			
				try:
					elm = ELM(args)
					elm.process()
				
					st = open("statsFile.csv", "a")
				
					from pathlib import Path
					hdim = Path('C:\\Github Repo\\Desk-LM\\output_test\\dlm\\include\\RF_Params.h').stat().st_size
					cdim = Path('C:\\Github Repo\\Desk-LM\\output_test\\dlm\\source\\RF_Params.c').stat().st_size
					
					tempCDim += cdim
					tempHDim += hdim
					st.write(f'{hdim}, {cdim} \n')
					st.close()
				except ValueError as error:
					print(error)
			
			#append stat to array
			tempCDim = tempCDim / maxIter
			tempHDim = tempHDim / maxIter
			tempRate = tempRate / maxIter
			
			trees_arr.append(x)
			mDepth_arr.append(y)
			rate_arr.append(tempRate)
			cDim_arr.append(tempCDim)
			hDim_arr.append(tempHDim)
			
			tempRate = 0
			tempHDim = 0 
			tempCDim = 0
			
	
	#plot the data
'''
	#trees_arr, mDepth_arr = np.meshgrid(trees_arr, mDepth_arr)
	

	fig = pyplot.figure()
	ax = Axes3D(fig)


	ax.scatter(trees_arr, mDepth_arr, rate_arr)
	ax.set_xlabel('# Tree')
	ax.set_ylabel('Max Depth')
	ax.set_zlabel('Rate')
	#pyplot.show()
	pyplot.savefig('score.png')
	
	fig2 = pyplot.figure()
	ax2 = Axes3D(fig2)

	ax2.scatter(trees_arr, mDepth_arr, hDim_arr)
	ax2.set_xlabel('# Tree')
	ax2.set_ylabel('Max Depth')
	ax2.set_zlabel('.h Size')
	
	pyplot.savefig('h_dim.png')
	#pyplot.show()
	
	fig3 = pyplot.figure()
	ax3 = Axes3D(fig3)
	ax3.scatter(trees_arr, mDepth_arr, cDim_arr)
	ax3.set_xlabel('# Tree')
	ax3.set_ylabel('Max Depth')
	ax3.set_zlabel('.c Size')
	
	pyplot.savefig('c_dim.png')
	#pyplot.show()
'''
