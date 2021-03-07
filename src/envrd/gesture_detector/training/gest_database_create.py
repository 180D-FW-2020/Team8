#
#  File: gest_database_create.py
# 
#  Author: Thomas Kost
#  
#  Date: 02 March 2021
#  
#  @brief script usoing gesture runner to gather data
#

# import RPi.GPIO as GPIO
import sys
import IMU
import time
import pandas as pd
import numpy as np
sys.path.append("..")
sys.path.append("src/envrd/gesture_detector")
sys.path.append("../../../comms/mqtt")
from gesture_classifier_runner import *
from gest_classifier import GestClassifier


# CSV file paths
data_file = "../../../../data/gesture/training_data/new_meat_database.csv"
coefficients_file = "../../../../data/gesture/classifier_coeffs/ls_classifier_coeffs.csv"
bias_file = "../../../../data/gesture/classifier_coeffs/ls_classifier_bias.csv"

# Parameters
classes = ["left_swipe", "garbage"]
readings_per_sample = 14
num_samples = 50
window_length = 50 # samples per measurement

#irrelevant parameters for this script
overlap = 25
sample_freq = 30 #samples per second
username = ""

# initialize classifier and runner
classifier = GestClassifier(len(classes), readings_per_sample*num_samples,coefficients_file,bias_file,\
        np.arange(len(classes)),classes)
runner = IMUSampleObject(classifier,window_length,overlap,sample_freq,username)

# create database
data = runner.create_database(10)
data.to_csv(data_file, mode='a', header=False)
