##
 #  File: svm_training.py
 # 
 #  Author: Thomas Kost
 #  
 #  Date: 17 February 2021
 #  
 #  @brief soft svm trainer, will take in data and produce a set of CSVs corresponding to the
 #         coeficcients produced by our loss function
 #
import pandas as pd
import numpy as np
import cvxpy as cp


class soft_SVM_trainer:
    def __init__(self, K, M):
        self.K = K   # Number of classes
        self.M = M   # Number of features
        self.W = []  # hyperplane vectors
        self.w = []  # hyperplane offsets
        self.A = []  # classifier --> labels allocation mapping
        self.labels = []

    def train(self, train_data, train_label, backdoor=False):
        # get labels
        self.labels = np.unique(train_label)
        
        # generate allocation matrix
        self.A = build_allocation_matrix(self.K)
        
        # stop without training if W and w are loaded from a file
        if backdoor is True:
            return
        
        # clear existing classifier data
        self.W = []
        self.w = []

        # erase random points with probability p
        X = np.copy(train_data)
        #X[np.random.rand(*train_data.shape) < p] = 0
        
        for class_i in range(self.K):
            
            for class_j in range(class_i+1, self.K):
                
                # select the labels and keep the subset of data. points belonging to class i come first to make labeling easy
                ind_i = (train_label == self.labels[class_i])
                ind_j = (train_label == self.labels[class_j])
                X_subset = np.block([[X[ind_i,:]], [X[ind_j,:]]])
            
                # convert labels to +1 if they match label i, -1 if label j. X_subset is sorted so that the label j points are the last ones
                Y = np.ones(X_subset.shape[0])
                Y[-np.sum(ind_j):] = -1

                # set up LP
                c = cp.Variable(self.M)
                b = cp.Variable(1)
                En = cp.Variable(X_subset.shape[0])
                # objective = cp.Minimize(0.5 * cp.sum_squares(c) + 0.1*cp.norm(En, 1)) # detmine if using SVM
                objective = cp.Minimize(0.5 * cp.norm(c, 1) + 0.1*cp.norm(En, 1)) # detmine if using SVM
                constraints = [cp.multiply(Y, ((X_subset @ c) + b)) >= 1-En, En >= 0]  # detmine if using SVM
                prob = cp.Problem(objective, constraints)
                prob.solve(solver=cp.ECOS, max_iters=200, verbose=True)
                
                # store each classifier
                self.W.append(c.value)
                self.w.append(b.value)
            
        return
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


if __name__ == "__main__":

     # import datasets
    data_pd  = pd.read_csv("data/gesture/training_data/new_meat_database.csv")
    data = data_pd.to_numpy()
    train_dat = data[0:799,:]
    test_dat  = data[800:,:]

    training_data_only = train_dat[:,2:]
    training_labels_only = train_dat[:,1]
    testing_data_only = test_dat[:,2:]
    testing_labels_only = test_dat[:,1]
    
    # keep certain labels
    include_labels = [0, 1]
    K = len(include_labels)
    
    
    # try to classify without training
    w_pass = False
    W_pass = False
    Ww_pass = False 
    try:  # empty W and w
        failed_classifier = soft_SVM_trainer(K, training_data_only.shape[1])
        failed_classifier.f(failed_classifier.classify(testing_data_only))
    except ValueError:
        Ww_pass = True
        print('Training check all empty: pass.')
    try:  # empty W only
        failed_classifier = soft_SVM_trainer(K, training_data_only.shape[1])
        failed_classifier.w = [0]
        failed_classifier.f(failed_classifier.classify(testing_data_only))
    except ValueError:
        W_pass = True
        print('Training check W empty: pass.')
    try:  # empty w only
        failed_classifier = soft_SVM_trainer(K, training_data_only.shape[1])
        failed_classifier.W = [0]
        failed_classifier.f(failed_classifier.classify(testing_data_only))
    except ValueError:
        w_pass = True
        print('Training check w empty: pass.')
        
    assert(Ww_pass and W_pass and w_pass)
    print('All checks pass.')
    
    # create and train classifier
    classifier = soft_SVM_trainer(K, training_data_only.shape[1])
    train_from_file = False
    if train_from_file:
        classifier.W = [np.loadtxt('weights_14.csv')]
        classifier.w = [np.loadtxt('bias_14.csv')]
        classifier.train(training_data_only, training_labels_only, backdoor=True)
    else:
        classifier.train(training_data_only, training_labels_only)
    
    # test classifier
    reg_dat = testing_data_only
    predicted = classifier.f(classifier.classify(testing_data_only))

    # compute accuracy
    accuracy = np.sum(np.equal(predicted, testing_labels_only))/predicted.shape[0]
    print(f"Accuracy = {accuracy}")

    # save results
    save_results = False
    if save_results:
        np.savetxt('data/gesture/classifier_coeffs/ls_classifier_coeffs.csv', classifier.W[0])
        np.savetxt('data/gesture/classifier_coeffs/ls_classifier_bias.csv', classifier.w[0])
        print('Results saved.')
