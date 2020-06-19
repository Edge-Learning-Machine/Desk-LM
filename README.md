# Desk-LM
Desk-LM is a python environment for training machine learning models. It currently implements the following ML algorithms:

- `Linear SVM`
- `Decision Tree`
- `K-NN`
- `ANN`

We are extending the library to other algorithms, also unsupervised. Your voluntary contribution is welcome.

The user can specify a `.csv` dataset, an algorithm and a set of parameter values, so to train and select the best model and export it for use on edge devices, by exploiting the twin tool [`Micro-LM`](https://github.com/Edge-Learning-Machine/Micro-LM).

For `ANNs`, [`Desk-LM`](https://github.com/Edge-Learning-Machine/Desk-LM) outputs the model in `hdf5` file format, to be imported by `STM32 CubeAI`, together with .c and .h files for pre-processing and for testing the whole dataset performance on the microcontroller (STM32 Nucleo boards only).

For all the other algorithms, [`Desk-LM`](https://github.com/Edge-Learning-Machine/Desk-LM) produces .c and .h that will be used as source files in a [`Micro-LM`](https://github.com/Edge-Learning-Machine/Micro-LM) project for optimzed memory footprint on edge devices. They contain the parameters of the selected ML model.

We are working so that [`Desk-LM`](https://github.com/Edge-Learning-Machine/Desk-LM) will output .json files so to allow dynamic usage by microcontrollers.

## Reference article for more infomation
F., Sakr, F., Bellotti, R., Berta, A., De Gloria, "Machine Learning on Mainstream Microcontrollers," Sensors 2020, 20, 2638.
https://www.mdpi.com/1424-8220/20/9/2638

## Getting started

### Input

The command line expects the path to .json files specifying:
- dataset
- estimator
- preprocessing
- validation
- output

#### Dataset
-d <path_to_dataset_config>.json

The file has the following properties:
- path, path to the .csv dataset file 
- skip_rows, number of rows to be skipped before the column names
- skip_columns, array of names of the columns to be skipped
- target_column, name of the target column
- sep, .csv file separator string/char
- decimal, .csv file decimal number separator
- test_size, integer (number of samples for the test), or float (fraction of the total samples to be used as test)
- categorical_multiclass, boolean specifying whether the multiclass labels are categorical or not (i.e., ordinal)




Currently, we support SVM, K-nn, ANN, DT.

-d <dataset_name>. The software expects a <dataset_name>.csv file in ../datasets/

Numeric only datasets are accepted, by now.

We have tried the software with the following datasets:
Heart Disease UCI | Kaggle. Available online: http://www.kaggle.com/ronitf/heart-disease-uci 

Boero, L.; Cello, M.; Marchese, M.; Mariconti, E.; Naqash, T.; Zappatore, S. Statistical fingerprint—Based intrusion detection system (SF-IDS). Int. J. Commun. Syst. 2017, 30, e3225.

Fausto, A.; Marchese, M. Implementation Details to Reduce the Latency of an SDN Statistical Fingerprint-Based IDS. In Proceedings of the IEEE International Symposium on Advanced Electrical and Communication Technologies (ISAECT), Rome, Italy, 27–29 November 2019.

http://www.fizyka.umk.pl/kis-old/projects/datasets.html#Sonar 

Traffic, Driving Style and Road Surface Condition | Kaggle. Available online: http://www.kaggle.com/gloseto/traffic-driving-style-road-surface-condition

EnviroCar—Datasets—the Datahub. Available online: http://www.old.datahub.io/dataset/envirocar (accessed on 13 February 2020).

Massoud, R.; Poslad, S.; Bellotti, F.; Berta, R.; Mehran, K.; Gloria, A.D. A fuzzy logic module to estimate a driver’s fuel consumption for reality-enhanced serious games. Int. J. Serious Games 2018, 5, 45–62.

Massoud, R.; Bellotti, F.; Poslad, S.; Berta, R.; De Gloria, A. Towards a reality-enhanced serious game to promote eco-driving in the wild. In Games and Learning Alliance. GALA 2019. Lecture Notes in Computer Science; Liapis, A., Yannakakis, G., Gentile, M., Ninaus, M., Eds.; Springer: Berlin, Germany, 2019

Search for and download air quality data | NSW Dept of Planning, Industry and Environment. Available online: http://www.dpie.nsw.gov.au/air-quality/search-for-and-download-air-quality-data (accessed on 13 February 2020).



#### Configuration files
config.py exposes the characteristics of the dataset to be processed (e.g., what the target column is), and the parameters to be analyzed for the pre-processing (e.g., 'mle' algorithm for automatic PCA) and for the selected algorithm training and cross-validation.

For ANN only:
- ./config/\<ds_name\>/activeFuncs.dat specifies the various activation functions that could be used in all the layers
- ./config/\<ds_name\>/layerShape.dat specifies the possible shapes of the layers of the ANN.

### Output

In config.py the user can specify the export_dir variable, where all the files usable by Micro-LM (please see https://github.com/Edge-Learning-Machine/Micro-LM for usage instructions) will be exported. Particularly, the files will be outuput under: "export_dir/ds/source" and "export_dir/ds/include". Output files are also duplicated in the following directories:

#### Linear SVM / DT / K-NN 
In './out/source/' and in './out/include/', the .c and .h files are generated, that contain the selected model parameters, that need to be compiled in a Edge-LM project.

The same output is also provided under:
'./out/' + cfg.ds_name + '/include/' + cfg.algo.lower() + '/'

#### ANN
In "export_dir/ds/source" and './out/source/', the preprocess_params.c file is saved, together with .c file for dataset testing
In "export_dir/ds/include" and './out/include/', the preprocess_params.h file is saved, together with .h file for dataset testing and the ANN model in hdf5 format

The same output is also provided under:
'./out/' + cfg.ds_name + '/include/' + cfg.algo.lower()

##### Use an ANN in a CubeIDE project, using STM X-Cube-AI package (for STM32 Nucleo boards only): 
1- Load the generated .h5 model from DeskML into STM32CubeIDE and generate the code for your target board

2- Use the generated files in your project for pre-processing and/or dataset testing

#### Testing
if the nTests variable (config.py) is equal to 'full', testing_set (.c and .h files) is produced.
Otherwise, a minimal_testing_set (.c and .h files) is produced.
All these files are used by Micro-LM to test a whole dataset or part of it

### Log
./\<ds_name\>.log, log file for each dataset 

## Data type
float 32 data are used

## Run
python main.py -d <dataset_name> -a <algo_name>

## Package versions
Please see the Desk-LM.3.6.10.yml file. Python 3.6, and Keras 2.2.4, which is needed for importing the ANN model in Cube-AI

## License
This project is licensed under the MIT License - see the [LICENSE.md](https://github.com/Edge-Learning-Machine/Desk-LM-new/blob/master/LICENSE) file for details

