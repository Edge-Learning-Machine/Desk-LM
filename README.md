# Desk-LM
Desk-LM is a python environment for training machine learning models (and make predictions as well). It currently implements the following ML algorithms:

- `Linear SVM`
- `Decision Tree`
- `Random Forest `
- `K-NN`
- `ANN`
- `TripleES` Holt-Winters Triple Exponential Smoothing implementation for time series

We are extending the library to other algorithms, also unsupervised. Your voluntary contribution is welcome.

The user can specify a `.csv` dataset, an algorithm and a set of parameter values, so to train and select the best model and export it for use on edge devices, by exploiting the twin tool [`Micro-LM`](https://github.com/Edge-Learning-Machine/Micro-LM).

For `ANNs`, [`Desk-LM`](https://github.com/Edge-Learning-Machine/Desk-LM) outputs the model in `hdf5` file format, to be imported by `STM32 CubeAI`, together with .c and .h files for pre-processing and for testing the whole dataset performance on the microcontroller (STM32 Nucleo boards only).

For all the other algorithms, [`Desk-LM`](https://github.com/Edge-Learning-Machine/Desk-LM) produces .c and/or .h that will be used as source files in a [`Micro-LM`](https://github.com/Edge-Learning-Machine/Micro-LM) project for optimzed memory footprint on edge devices. They contain the parameters of the selected ML model.

[`Desk-LM`](https://github.com/Edge-Learning-Machine/Desk-LM) relies on numpy, pandas, sk-learn and keras/Tensorflow.

We are working so that [`Desk-LM`](https://github.com/Edge-Learning-Machine/Desk-LM) will output .json files so to allow dynamic usage by microcontrollers.

## Getting started

### Input

The command line expects the path to .json files specifying:
- dataset
- estimator
- preprocessing
- validation
- output
- prediction
- storage

#### Dataset configuration
**-d <path_to_dataset_config_file>**

The .json config file exposes the following properties:
- path, path to the .csv dataset file 
- skip_rows, number of rows to be skipped before the column names
- select_columns, array of names of the columns to be selected as features (all the others are discarded)
- select_columns, if true, means that all columns are selected
- skip_columns, array of names of the columns to be skipped (ignored, if select_feature_columns is set)
- target_column, name of the target column
- time_series_column, name of the column for the time series. It is used only for time series computation and is mutually exclusive with all the other column options 
- sep, .csv file separator string/char
- decimal, .csv file decimal number separator
- test_size, integer (number of samples for the test), or float (fraction of the total samples to be used as test)
- categorical_multiclass, boolean specifying whether the multiclass labels are categorical or not (i.e., ordinal)

#### Estimator configuration
**-e <path_to_estimator_config_file>**

The .json config file exposes the following properties:
- estimator, name of the estimator. If not differently stated, all estimators are implemented through sk-learn. Currently supported estimators are:
  - KNeighborsClassifier
  - KNeighborsRegressor
  - DecisionTreeClassifier
  - DecisionTreeRegressor
  - LinearSVC
  - LinearSVR
  - ANNClassifier, Keras/Tensorflow implementation
  - ANNRegressor, Keras/Tensorflow implementation
  - TripleES, the Holt-Winters Triple Exponential Smoothing for time series

Each estimator type has its own configuration parameters:
- k-NN
  - n_neighbors (*), default: 5 
- DecisionTree
  - max_depth (*), default: None
  - min_samples_split (*), default: 2 
  - min_samples_leaf (*), default: 1
  - max_leaf_nodes (*), default: None 
- SVC/SVR
  - C_exp (*), exponent of the C parameter, default 0
- ANN
  - epochs (*), default: 10
  - batch_size (*), default: 32 
  - dropout (*), float between 0 and 1, default: 0
  - activation, array of strings (e.g., "relu", "tanh") for the activation function of the hidden layers, default: "relu"
  - hidden_layers, array of array of integers representing the size of each hidden layer, default: []. Each inner array represents one ANN layer configuration (i.e., number of nodes for each layer) among those to be evaluated in the cross-validation
- TripleES
  - season_length

(*) for the sake of model selection and cross validation, for this property <prop> it is possible to specify (all values are integers, if not differently specified, as ANN dropout):
- < prop >, a single value
- <prop_array>, an array of values
- <lower_limit>, a lower_limit for a value range
- <upper_limit>, a upper_limit for a value range
- < step >, step for a value range

Please refer to sk-learn and keras documentation for the details on the configuration parameters.

#### Preprocessing configuration
**-p <path_to_preprocessing_config_file>**

The .json config file exposes the following properties:
- scale, array of strings specifying scalers (currently supported scalers: "StandardScaler", "MinMaxScaler"), default: no scaler
- pca_values, array of numbers (integer or float between 0 and 1) representing the principal components. It is possible to specify also the string "mle", default: no PCA 

Not used for TripleES.

Please refer to sk-learn documentation for further details.

#### Model selection configuration
**-s <path_to_model_selection_config_file>**

The .json config file exposes the following properties:
- cv, cross validation schema, default: None, to use the default 5-fold cross validation 
- scoring, scoring method for cross validation
  - Regression problem, possible values:
    - "mean_absolute_error"
    - "mean_squared_error", default value for ANN
    - "mean_squared_log_error'
    - "root_mean_squared_error"
    - "r2", default value for k-NN, LinearSVR, DecisionTree
  - Classification problem, possible values:
    - "accuracy", which is the default value
    - "balanced_accuracy"
    - "f1", "f1_micro", "f1_macro", "f1_samples", "f1_weighted"
    - "precision", "precision_micro", "precision_macro", "precision_samples", "precision_weighted"
    - "recall", "recall_micro", "recall_macro", "recalln_samples", "recall_weighted"
- verbose, verbosity level, default: 0

Please refer to sk-learn documentation for further details.

#### Output configuration
**-o <path_to_output_config_file>**

The .json file exposes the following properties:
- export_path, path to a directory where to export the output folders, default: no export. Output folders are structured like this:
  - elm/source, for .c files
  - elm/include, for .h files
  - elm/model, for models, such as the ANN .h5 file
- is_dataset_test, if files for a whole dataset test on the target devices are to be prepared, default: no dataset test (i.e., one shot estimation only)
- dataset_test_size, sets a limit to the number of testing records to be exported for the dataset test. Can be either int (number of records) or float (0-1 - percentage of the desktop test set), default: 1
- training_set_cap, for k-NN, sets a limit to the number of training samples to be exported for the k-NN estimation. Can be either int (number of samples) or float (0-1), default: no cap 

#### Prediction configuration
**--predict <path_to_predict_config_file>**

The .json file exposes the following properties:
- model_id, the uuid of the model to be loaded on the server to make the prediction
- samples, an array of samples for which to build the prediction

#### Storage configuration
**--store**

The program stores the estimator in the "./storage/" directory. It provides an uuid for future retrieval for predictions

### Run
- For computing a model and generating files for deployment on Micro-LM (or an .h5 file for neural networks)
python main.py -d <dataset_config_file> -e <estimator_config_file> -p <preprocessing_config_file> -s <model_selection_config_file> -o <output_config_file>

- For computing and storing a model
python main.py -d <dataset_config_file> -e <estimator_config_file> -p <preprocessing_config_file> -s <model_selection_config_file> --store

- For predicting a set of samples with a trained model
python main.py --predict <predict_config_file>

## Output
Output files are also produced under the `out` diectory, with the following structure:
- out/source, for .c files
- out/include, for .h files
- out/model, for models, such as the ANN .h5 file

The structure is duplicated in the `elm` export directory, if specified in the output configuration file.

### Linear SVM / DT / K-NN / TripleES
For using source and header files produced by Desk-LM for these algorithms, please refer to the [`Micro-LM`](https://github.com/Edge-Learning-Machine/Micro-LM) documentation.

### Use a Desk-LM ANN in a CubeIDE project, using STM X-Cube-AI package (for STM32 Nucleo boards only): 
1. Load the .h5 model generated by DeskML into STM32CubeIDE and generate the code for your target board
2. Add to your CubeIDE project the files generated by Desk-LM for pre-processing and/or dataset testing (source/preprocess_params.c and source/testing_set.c and include/PPParmas.h and include/testing_set.h).
3. You need to add also ELM.h and Preprocess.c and Preprocess.h from [`Micro-LM`](https://github.com/Edge-Learning-Machine/Micro-LM).
4. Use function *preprocess(X)*, exposed by ELM.h, where X is the sample vector for preprocessing

## Examples
Example .json files are provided in the input dirctory. We adopt the following convention:
- *ds_* is the prefix for dataset configuration files.
- *pp_* for preprocessing
- *est_* for estimator
- *ms_* for model selection
- *output_* for output
- *pr_* for predicting

Example .csv files are provided in the ./dataset/ directory.
- Heart Disease UCI | Kaggle. Available online: http://www.kaggle.com/ronitf/heart-disease-uci
- Traffic, Driving Style and Road Surface Condition | Kaggle. Available online: http://www.kaggle.com/gloseto/traffic-driving-style-road-surface-condition
- Appliances energy prediction | UCI. Available online: https://data.world/uci/appliances-energy-prediction
- Ads timeseries | Kaggle. Available online: https://www.kaggle.com/kashnitsky/topic-9-part-1-time-series-analysis-in-python?select=ads.csv

## Data type
float 32 data are used

## Package versions
Please see the Desk-LM.3.6.10.yml file. Python 3.6, and Keras 2.2.4, which is needed for importing the ANN model in Cube-AI

## License
This project is licensed under the MIT License - see the [LICENSE.md](https://github.com/Edge-Learning-Machine/Desk-LM/blob/master/LICENSE.md) file for details

## Contributing
Please see [CONTRIBUTING.md](https://github.com/Edge-Learning-Machine/Desk-LM/blob/master/docs/CONTRIBUTING.md)


Credits:
- `Alessio Capello` for Random Forest implementation;
- `Gabriele Campodonico` for TripleES implementation;
- `Laura Pisano` for TripleES implementation;

## Reference article for more infomation
F., Sakr, F., Bellotti, R., Berta, A., De Gloria, "Machine Learning on Mainstream Microcontrollers," Sensors 2020, 20, 2638.
https://www.mdpi.com/1424-8220/20/9/2638


## References
Credit for the Holt-Winters Triple Exponential Smoothing implementation for time series: https://medium.com/open-machine-learning-course/open-machine-learning-course-topic-9-time-series-analysis-in-python-a270cb05e0b3
