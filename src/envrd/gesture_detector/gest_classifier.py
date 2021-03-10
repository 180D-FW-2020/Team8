##
 #  File: gest_classifier.py
 # 
 #  Author: Thomas Kost
 #  
 #  Date: 04 December 2020
 #  
 #  @brief classifier object for gestures
 #
 
import sys
sys.path.append('src/envrd/gesture_detector/training/calibrateBerryIMU.py')
sys.path.append('training')
from svm_classifier import soft_SVM_classifier as svm

class GestClassifier:
    def __init__(self, num_classes, num_features, hyperplane_coeffs_csv_path, hyperplane_offsets_csv_path,labels, gest_names):
        self.classifier = svm(num_classes, num_features,hyperplane_coeffs_csv_path, hyperplane_offsets_csv_path, labels)
        self.gest_dict = dict(zip(labels,gest_names))
        
    def __classify(self, data):
        '''
        parameters:
        - data: array of length num_features corresponding to a reading

        Returns:
        - integer label corresponding to label of most probable classification
        '''
        return self.classifier.f(self.classifier.classify(data))

    def classify_action(self, data):
        '''
        parameters:
        - data: array of length num_features corresponding to a reading

        Returns:
        - string label corresponding to label of most probable classification
        '''
        return self.gest_dict[self.__classify(data)[0]]
