import json
import jsonschema
from jsonschema import validate

import abc

import error as error
from Estimator import Estimator


class RandomForest(Estimator):
	def __init__(self, jsonData):
		super().__init__()
		self.nick = 'rf'
		try:
			with open('schemas/rfSchema.json') as schema_file:
				rfSchema = json.load(schema_file)
		except FileNotFoundError as err:
			template = "An exception of type {0} occurred. Arguments: {1!r}"
			message = template.format(type(err).__name__, err.args)
			print(message)
			raise ValueError(error.errors['rf_config'])
		try:
			validate(instance=jsonData, schema=rfSchema)
		except jsonschema.exceptions.ValidationError as err:
			template = "An exception of type {0} occurred. Arguments: {1!r}"
			message = template.format(type(err).__name__, err.args)
			print(message)
			raise ValueError(error.errors['rf_config'])
		self.parse(jsonData)

	def parse(self, jsonData):
		if jsonData['estimator'].endswith('Classifier'):
			from sklearn.ensemble import RandomForestClassifier
			self.estimator = RandomForestClassifier(criterion='gini')
			self.is_regr = False
		else:
			from sklearn.ensemble import RandomForestRegressor
			self.estimator = RandomForestRegressor(criterion='mse')
			self.is_regr = True
		self.params = {}
        
		import sys
		sys.path.insert(1, 'utils')
		import dict_utils
		self.params['n_estimators'] = dict_utils.parse_related_properties('n_estimators', jsonData, 100)
		self.params['max_depth'] = dict_utils.parse_related_properties('max_depth', jsonData, None)
		self.params['min_samples_split'] = dict_utils.parse_related_properties('min_samples_split', jsonData, 2)
		self.params['min_samples_leaf'] = dict_utils.parse_related_properties('min_samples_leaf', jsonData, 1)
		self.params['min_weight_fraction_leaf'] = dict_utils.parse_related_properties('min_weight_fraction_leaf', jsonData, 0.0)
		self.params['max_features'] = dict_utils.parse_related_properties('max_features', jsonData, 'auto')
		self.params['max_leaf_nodes'] = dict_utils.parse_related_properties('max_leaf_nodes', jsonData, None)
		self.params['min_impurity_decrease'] = dict_utils.parse_related_properties('min_impurity_decrease', jsonData, 0.0)
		self.params['n_jobs'] = dict_utils.parse_related_properties('n_jobs', jsonData, None)
		self.params['verbose'] = dict_utils.parse_related_properties('verbose', jsonData, 0)
		
        
		sys.path.insert(1, 'output')
		import RandomForest_OM
		self.output_manager = RandomForest_OM.RandomForest_OM(self)