#ifndef RF_PARAMS_H
#define RF_PARAMS_H

#define FOREST_DIM 10

#define N_CLASS 2

/// VARIABLES FOR TREE NUMBER 0 

#define N_NODES_t0 83

#define VALUES_DIM_t0 2

extern int children_left_t0[N_NODES_t0];
extern int children_right_t0[N_NODES_t0];
extern int feature_t0[N_NODES_t0];
extern float threshold_t0[N_NODES_t0];
extern int values_t0[N_NODES_t0][VALUES_DIM_t0];


/// VARIABLES FOR TREE NUMBER 1 

#define N_NODES_t1 97

#define VALUES_DIM_t1 2

extern int children_left_t1[N_NODES_t1];
extern int children_right_t1[N_NODES_t1];
extern int feature_t1[N_NODES_t1];
extern float threshold_t1[N_NODES_t1];
extern int values_t1[N_NODES_t1][VALUES_DIM_t1];


/// VARIABLES FOR TREE NUMBER 2 

#define N_NODES_t2 89

#define VALUES_DIM_t2 2

extern int children_left_t2[N_NODES_t2];
extern int children_right_t2[N_NODES_t2];
extern int feature_t2[N_NODES_t2];
extern float threshold_t2[N_NODES_t2];
extern int values_t2[N_NODES_t2][VALUES_DIM_t2];


/// VARIABLES FOR TREE NUMBER 3 

#define N_NODES_t3 91

#define VALUES_DIM_t3 2

extern int children_left_t3[N_NODES_t3];
extern int children_right_t3[N_NODES_t3];
extern int feature_t3[N_NODES_t3];
extern float threshold_t3[N_NODES_t3];
extern int values_t3[N_NODES_t3][VALUES_DIM_t3];


/// VARIABLES FOR TREE NUMBER 4 

#define N_NODES_t4 85

#define VALUES_DIM_t4 2

extern int children_left_t4[N_NODES_t4];
extern int children_right_t4[N_NODES_t4];
extern int feature_t4[N_NODES_t4];
extern float threshold_t4[N_NODES_t4];
extern int values_t4[N_NODES_t4][VALUES_DIM_t4];


/// VARIABLES FOR TREE NUMBER 5 

#define N_NODES_t5 87

#define VALUES_DIM_t5 2

extern int children_left_t5[N_NODES_t5];
extern int children_right_t5[N_NODES_t5];
extern int feature_t5[N_NODES_t5];
extern float threshold_t5[N_NODES_t5];
extern int values_t5[N_NODES_t5][VALUES_DIM_t5];


/// VARIABLES FOR TREE NUMBER 6 

#define N_NODES_t6 89

#define VALUES_DIM_t6 2

extern int children_left_t6[N_NODES_t6];
extern int children_right_t6[N_NODES_t6];
extern int feature_t6[N_NODES_t6];
extern float threshold_t6[N_NODES_t6];
extern int values_t6[N_NODES_t6][VALUES_DIM_t6];


/// VARIABLES FOR TREE NUMBER 7 

#define N_NODES_t7 97

#define VALUES_DIM_t7 2

extern int children_left_t7[N_NODES_t7];
extern int children_right_t7[N_NODES_t7];
extern int feature_t7[N_NODES_t7];
extern float threshold_t7[N_NODES_t7];
extern int values_t7[N_NODES_t7][VALUES_DIM_t7];


/// VARIABLES FOR TREE NUMBER 8 

#define N_NODES_t8 95

#define VALUES_DIM_t8 2

extern int children_left_t8[N_NODES_t8];
extern int children_right_t8[N_NODES_t8];
extern int feature_t8[N_NODES_t8];
extern float threshold_t8[N_NODES_t8];
extern int values_t8[N_NODES_t8][VALUES_DIM_t8];


/// VARIABLES FOR TREE NUMBER 9 

#define N_NODES_t9 97

#define VALUES_DIM_t9 2

extern int children_left_t9[N_NODES_t9];
extern int children_right_t9[N_NODES_t9];
extern int feature_t9[N_NODES_t9];
extern float threshold_t9[N_NODES_t9];
extern int values_t9[N_NODES_t9][VALUES_DIM_t9];


/// Arrays for the whole forest to make it easier to use 

extern int* forest_children_left[FOREST_DIM];
extern int* forest_children_right[FOREST_DIM];
extern int* forest_feature[FOREST_DIM];
extern float* forest_threshold[FOREST_DIM];
extern int** forest_values[FOREST_DIM];

#endif