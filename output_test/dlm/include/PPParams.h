#ifndef PPPARAMS_H
#define PPPARAMS_H

#ifndef PCA_N_FEATURE
#define PCA_N_FEATURE 1
#endif

#ifndef PCA_N_ORIG_FEATURE
#define PCA_N_ORIG_FEATURE 2
#endif

extern float pca_components[PCA_N_FEATURE][PCA_N_ORIG_FEATURE];

#define MINMAX_SCALING

extern float s_x[PCA_N_ORIG_FEATURE];
#endif