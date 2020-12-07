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
sys.path.append('../../training/classifier_training')
from soft_SVM import soft_SVM as svm
sys.path.remove('../../training/classifier_training')

class GestClassifier:
    def __init__(self, num_classes, num_features, coeficcient_weights_file, bias_weight_file, gest_names = None)
        self.classifier = svm(num_classes, num_features)
        self.num_classes = num_classes
        self.num_features = num_features
        self.classifier.W = [np.loadtxt(coeficcient_weights_file)]
        self.classifier.w = [np.loadtxt(bias_weight_file)]
        self.classifier.train(None, None, backdoor=True)
        self.gest_names = gest_names
    def classify(self, data)
        return self.classifier.classify(data)

