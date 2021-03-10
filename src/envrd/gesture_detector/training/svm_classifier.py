##
 #  File: svm_classifier.py
 # 
 #  Author: Thomas Kost
 #  
 #  Date: 17 February 2021
 #  
 #  @brief svm classifier, will only perform classification and is not dependent on cvxpy
 #         (indended for running on raspberry pi using pretrined coefficients)
 #

import pandas as pd
import numpy as np

class soft_SVM_classifier:
    def __init__(self, K: int, M : int , hyperplane_coeffs_csv_path : str ,hyperplane_offsets_csv_path : str, labels : list ):
        self.K = K   # Number of classes
        self.M = M   # Number of features
        self.W = [np.loadtxt(hyperplane_coeffs_csv_path)]  # hyperplane vectors
        self.w = [np.loadtxt(hyperplane_offsets_csv_path)]  # hyperplane offsets
        self.A = build_allocation_matrix(self.K)  # classifier --> labels allocation mapping
        self.labels = np.unique(np.asarray(labels))

    def f(self, test_results):
        # The inputs of this function are:
        #
        # inp: the input to the function f(*), equal to g(y) = W^T y + w
        #
        # The outputs of this function are:
        #
        # s: this should be a scalar equal to the class estimated from
        # the corresponding input data point, equal to f(W^T y + w)
        # You should also check if the classifier is trained i.e. self.W and
        # self.w are nonempty
            
        test_results_sign = np.sign(test_results)
        y_hat = test_results_sign @ self.A.T
        s_labels = self.labels[np.argmax(y_hat, axis=1)]

        return s_labels
        
    def classify(self, test_data):
        # check that classifier is trained
        if not self.W or not self.w:
            raise ValueError('Classifier is not trained.') 

        num_class = self.K*(self.K-1)//2
            
        test_results = np.empty([test_data.shape[0], num_class])
        for classifier in range(num_class):
            test_results[:,classifier] = np.inner(self.W[classifier], test_data) + self.w[classifier]
            
        return test_results

def build_allocation_matrix(n):
    """
    Recursive function that builds the allocation matrix for translating
    one-vs-one classifier outputs into labels.
    Parameters
    ----------
    n : int
        number of labels
    Returns
    -------
    np.array of dimension (n x n*(n-1)/2) which is a mapping from one-vs-one
    classifier outputs to labels. The index of the predicted label is the
    argmax of this matrix multiplied by the prediction vector
    """
    if n == 2:
        return np.array([[1, -1]]).T
    else:
        return np.block([[np.ones((1,n-1)), np.zeros((1,(n-1)*(n-2)//2))],
                        [-np.eye(n-1), build_allocation_matrix(n-1)]])
                        