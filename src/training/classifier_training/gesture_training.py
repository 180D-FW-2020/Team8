##
 #  File: gesture_training.py
 # 
 #  Author: Thomas Kost
 #  
 #  Date: 15 November 2020
 #  
 #  @brief train gesture recognition using the gesutre_recognition_data.csv file
 #

from soft_SVM import soft_SVM as svm
import numpy as np
import pandas as pd

# import datasets

train_dat = pd.read_csv("src/training/training_data/meat_gesture_database_training_fixed.csv")
test_dat = pd.read_csv("src/training/training_data/meat_gesture_database_testing_fixed.csv")

train_dat = train_dat.dropna(axis='columns')
test_dat = test_dat.dropna(axis='columns')
# keep certain labels
include_labels = [0, 1]
# train_dat = train_dat[train_dat.label.isin(include_labels)]
# test_dat = test_dat[test_dat.label.isin(include_labels)]
K = len(include_labels)

# convert from pd dataframe to numpy array
train_dat = train_dat.to_numpy()
test_dat = test_dat.to_numpy()

# rearrange 
temp = test_dat
test_dat = train_dat[400:,:]
train_dat[400:,:] = temp
# split into data and labels
training_data_only = train_dat[:,2:]
training_labels_only = train_dat[:,1]
testing_data_only = test_dat[:,2:]
testing_labels_only = test_dat[:,1]

# try to classify without training
w_pass = False
W_pass = False
Ww_pass = False
try:  # empty W and w
    failed_classifier = svm(K, training_data_only.shape[1])
    failed_classifier.f(failed_classifier.classify(testing_data_only))
except ValueError:
    Ww_pass = True
    print('Training check all empty: pass.')
try:  # empty W only
    failed_classifier = svm(K, training_data_only.shape[1])
    failed_classifier.w = [0]
    failed_classifier.f(failed_classifier.classify(testing_data_only))
except ValueError:
    W_pass = True
    print('Training check W empty: pass.')
try:  # empty w only
    failed_classifier = svm(K, training_data_only.shape[1])
    failed_classifier.W = [0]
    failed_classifier.f(failed_classifier.classify(testing_data_only))
except ValueError:
    w_pass = True
    print('Training check w empty: pass.')
    
assert(Ww_pass and W_pass and w_pass)
print('All checks pass.')

# create and train classifier
classifier = svm(K, training_data_only.shape[1])
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
predicted_on_training = classifier.f(classifier.classify(training_data_only))
# compute accuracy
train_accuracy = np.sum(np.equal(predicted_on_training, training_labels_only))/predicted_on_training.shape[0]
accuracy = np.sum(np.equal(predicted, testing_labels_only))/predicted.shape[0]
print(f"Accuracy = {accuracy}")
print(f"Training Accuracy = {train_accuracy}")

# save results
save_results = True
if save_results:
    np.savetxt('src/training/classifier_coeffs/left_swipe_classifier_coeffs.csv', classifier.W[0])
    np.savetxt('src/training/classifier_coeffs/left_swipe_classifier_bias.csv', classifier.w[0])
    print('Results saved.')

  