X_test = self.predict.samples
estimator = m['esti']
#scaler = m['scale']
#X_test = scaler.transform(X_test)

'''
            for name, transform in m.steps[:-1]:
                #if transform is not None:
                #    Xt = transform.transform(Xt)
                if name == 'scale':
                    X_test = transform.transform(X_test)
                if name == 'reduce_dims':
                    X_test = transform.transform(X_test)
                    break
            '''

pca = m['reduce_dims']

mySample = X_test[0]
transf = np.dot(pca.components_, mySample-pca.mean_)
print(transf)

X_test = pca.transform(X_test)
print(X_test)

n_nodes = estimator.tree_.node_count
children_left = estimator.tree_.children_left
children_right = estimator.tree_.children_right
feature = estimator.tree_.feature
threshold = estimator.tree_.threshold
values = estimator.tree_.value

# The tree structure can be traversed to compute various properties such
# as the depth of each node and whether or not it is a leaf.
node_depth = np.zeros(shape=n_nodes, dtype=np.int64)
 is_leaves = np.zeros(shape=n_nodes, dtype=bool)
  stack = [(0, -1)]  # seed is the root node id and its parent depth
   while len(stack) > 0:
        node_id, parent_depth = stack.pop()
        node_depth[node_id] = parent_depth + 1

        # If we have a test node
        if (children_left[node_id] != children_right[node_id]):
            stack.append((children_left[node_id], parent_depth + 1))
            stack.append((children_right[node_id], parent_depth + 1))
        else:
            is_leaves[node_id] = True

    print("The binary tree structure has %s nodes and has "
          "the following tree structure:"
          % n_nodes)
    for i in range(n_nodes):
        if is_leaves[i]:
            print("%snode=%s leaf node." % (node_depth[i] * "\t", i))
        else:
            print("%snode=%s test node: go to node %s if X[:, %s] <= %s else to "
                  "node %s."
                  % (node_depth[i] * "\t",
                     i,
                     children_left[i],
                     feature[i],
                     threshold[i],
                     children_right[i],
                     ))
    print()

    # First let's retrieve the decision path of each sample. The decision_path
    # method allows to retrieve the node indicator functions. A non zero element of
    # indicator matrix at the position (i, j) indicates that the sample i goes
    # through the node j.

    node_indicator = estimator.decision_path(X_test)

    # Similarly, we can also have the leaves ids reached by each sample.

    leave_id = estimator.apply(X_test)

    # Now, it's possible to get the tests that were used to predict a sample or
    # a group of samples. First, let's make it for the sample.

    for sample_id in range(len(X_test)):
        node_index = node_indicator.indices[node_indicator.indptr[sample_id]:
                                            node_indicator.indptr[sample_id + 1]]

        print('Rules used to predict sample %s: ' % sample_id)
        for node_id in node_index:
            if leave_id[sample_id] == node_id:
                print("decision id node %s : is %s" %
                      (node_id, np.argmax(values[node_id])))
                continue

            if (X_test[sample_id][feature[node_id]] <= threshold[node_id]):
                threshold_sign = "<="
            else:
                threshold_sign = ">"

            print("decision id node %s : (X_test[%s, %s] (= %s) %s %s)"
                  % (node_id,
                     sample_id,
                     feature[node_id],
                     X_test[sample_id][feature[node_id]],
                     threshold_sign,
                     threshold[node_id]))
