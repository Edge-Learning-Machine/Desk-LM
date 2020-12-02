#ifndef RF_PARAMS_H
#define RF_PARAMS_H

#define FOREST_DIM 10

/// VARIABLES FOR TREE NUMBER 0 

#define N_NODES_t0 7

#define VALUES_DIM_t0 2

#define N_CLASS 2
#define N_LEAVES_t0 4

#define VALUES_DIM 2

extern int children_left_t0[N_NODES_t0];
extern int children_right_t0[N_NODES_t0];
extern int feature_t0[N_NODES_t0];
extern float threshold_t0[N_NODES_t0];
extern int leaf_nodes_t0[N_LEAVES_t0][2+VALUES_DIM];
/// VARIABLES FOR TREE NUMBER 1 

#define N_NODES_t1 7

#define VALUES_DIM_t1 2

#define N_CLASS 2
#define N_LEAVES_t1 4

#define VALUES_DIM 2

extern int children_left_t1[N_NODES_t1];
extern int children_right_t1[N_NODES_t1];
extern int feature_t1[N_NODES_t1];
extern float threshold_t1[N_NODES_t1];
extern int leaf_nodes_t1[N_LEAVES_t1][2+VALUES_DIM];
/// VARIABLES FOR TREE NUMBER 2 

#define N_NODES_t2 7

#define VALUES_DIM_t2 2

#define N_CLASS 2
#define N_LEAVES_t2 4

#define VALUES_DIM 2

extern int children_left_t2[N_NODES_t2];
extern int children_right_t2[N_NODES_t2];
extern int feature_t2[N_NODES_t2];
extern float threshold_t2[N_NODES_t2];
extern int leaf_nodes_t2[N_LEAVES_t2][2+VALUES_DIM];
/// VARIABLES FOR TREE NUMBER 3 

#define N_NODES_t3 7

#define VALUES_DIM_t3 2

#define N_CLASS 2
#define N_LEAVES_t3 4

#define VALUES_DIM 2

extern int children_left_t3[N_NODES_t3];
extern int children_right_t3[N_NODES_t3];
extern int feature_t3[N_NODES_t3];
extern float threshold_t3[N_NODES_t3];
extern int leaf_nodes_t3[N_LEAVES_t3][2+VALUES_DIM];
/// VARIABLES FOR TREE NUMBER 4 

#define N_NODES_t4 7

#define VALUES_DIM_t4 2

#define N_CLASS 2
#define N_LEAVES_t4 4

#define VALUES_DIM 2

extern int children_left_t4[N_NODES_t4];
extern int children_right_t4[N_NODES_t4];
extern int feature_t4[N_NODES_t4];
extern float threshold_t4[N_NODES_t4];
extern int leaf_nodes_t4[N_LEAVES_t4][2+VALUES_DIM];
/// VARIABLES FOR TREE NUMBER 5 

#define N_NODES_t5 7

#define VALUES_DIM_t5 2

#define N_CLASS 2
#define N_LEAVES_t5 4

#define VALUES_DIM 2

extern int children_left_t5[N_NODES_t5];
extern int children_right_t5[N_NODES_t5];
extern int feature_t5[N_NODES_t5];
extern float threshold_t5[N_NODES_t5];
extern int leaf_nodes_t5[N_LEAVES_t5][2+VALUES_DIM];
/// VARIABLES FOR TREE NUMBER 6 

#define N_NODES_t6 7

#define VALUES_DIM_t6 2

#define N_CLASS 2
#define N_LEAVES_t6 4

#define VALUES_DIM 2

extern int children_left_t6[N_NODES_t6];
extern int children_right_t6[N_NODES_t6];
extern int feature_t6[N_NODES_t6];
extern float threshold_t6[N_NODES_t6];
extern int leaf_nodes_t6[N_LEAVES_t6][2+VALUES_DIM];
/// VARIABLES FOR TREE NUMBER 7 

#define N_NODES_t7 7

#define VALUES_DIM_t7 2

#define N_CLASS 2
#define N_LEAVES_t7 4

#define VALUES_DIM 2

extern int children_left_t7[N_NODES_t7];
extern int children_right_t7[N_NODES_t7];
extern int feature_t7[N_NODES_t7];
extern float threshold_t7[N_NODES_t7];
extern int leaf_nodes_t7[N_LEAVES_t7][2+VALUES_DIM];
/// VARIABLES FOR TREE NUMBER 8 

#define N_NODES_t8 7

#define VALUES_DIM_t8 2

#define N_CLASS 2
#define N_LEAVES_t8 4

#define VALUES_DIM 2

extern int children_left_t8[N_NODES_t8];
extern int children_right_t8[N_NODES_t8];
extern int feature_t8[N_NODES_t8];
extern float threshold_t8[N_NODES_t8];
extern int leaf_nodes_t8[N_LEAVES_t8][2+VALUES_DIM];
/// VARIABLES FOR TREE NUMBER 9 

#define N_NODES_t9 7

#define VALUES_DIM_t9 2

#define N_CLASS 2
#define N_LEAVES_t9 4

#define VALUES_DIM 2

extern int children_left_t9[N_NODES_t9];
extern int children_right_t9[N_NODES_t9];
extern int feature_t9[N_NODES_t9];
extern float threshold_t9[N_NODES_t9];
extern int leaf_nodes_t9[N_LEAVES_t9][2+VALUES_DIM];
extern int target_classes[N_CLASS];


/// Arrays for the whole forest to make it easier to use 

extern int target_classes[N_CLASS];
extern int forest_nodes[FOREST_DIM];
extern int* forest_children_left[FOREST_DIM];
extern int* forest_children_right[FOREST_DIM];
extern int* forest_feature[FOREST_DIM];
extern float* forest_threshold[FOREST_DIM];
extern int* forest_leaves[FOREST_DIM];

#endif