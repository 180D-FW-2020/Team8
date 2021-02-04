################################################
# File Name: gest_classifer_runner.py
# 
# Author: Thomas Kost
# 
# Date: February 3, 2021
#
# Brief: runs the gesture classifier: handling classifcation, sampling, and communication
#
###############################################
import sys
import threading
from gest_classifier import GestClassifier
sys.path.append('./training/classifier_training')
sys.path.append('../../../data/gesture/classifier_coeffs')
sys.path.append('../../comms/mqtt')
import IMU
import RPi.GPIO as GPIO
import time
import pandas as pd
import numpy as np
import mqtt_link as mqtt
sys.path.remove('./training/classifier_training')
sys.path.remove('../../../data/gesture/classifier_coeffs')
sys.path.remove('../../comms/mqtt')


class IMUSampleObject:

    def __init__(self,classes, window_length, overlap, sample_period, weights_file, bias_file, username, gest_names):
        self.window_length = window_length #number of Samples
        self.length_sample = 6
        self.classifier    = GestClassifier(classes,self.length_sample*window_length,weights_file, bias_file, gest_names)
        self.data    = [None]*self.length_sample*window_length
        self.reading = [None]*self.length_sample*overlap
        self.overlap = overlap
        self.samples_taken = 0
        self.sample_period = sample_period
        self.gest_names = gest_names
        # Setup Server Link
        self.board = "ece180d/MEAT/general/gesture"
        self.user = "raspberry_controller_" + username
        self.mqtt_server = mqtt.MQTTLink( self.board, self.user)
        self.designated_reciever = username

        #initialize sensor
        IMU.detectIMU()
        if(IMU.BerryIMUversion == 99):
            print(" No BerryIMU found...sick nasty")
            sys.exit()
        IMU.initIMU() # initialize all the relevant sensors

    def sample(self):
        ACCx = IMU.readACCx()
        ACCy = IMU.readACCy()
        ACCz = IMU.readACCz()
        GYRx = IMU.readGYRx()
        GYRy = IMU.readGYRy()
        GYRz = IMU.readGYRz()

        self.reading[self.samples_taken*self.length_sample]      = ACCx
        self.reading[self.samples_taken*self.length_sample + 1 ] = ACCy
        self.reading[self.samples_taken*self.length_sample + 2 ] = ACCz
        self.reading[self.samples_taken*self.length_sample + 3 ] = GYRx
        self.reading[self.samples_taken*self.length_sample + 4 ] = GYRy
        self.reading[self.samples_taken*self.length_sample + 5 ] = GYRz
        
        self.samples_taken += 1

        if not(self.samples_taken % self.overlap):
            self.data = np.roll(self.data, (self.window_length - self.overlap)*6)
            self.data[-self.overlap:] = self.reading
            self.samples_taken = 0
            result = self.classifier.classify(self.data) #TODO make event triggering on this result

            # apply result to mqtt link
            if self.gest_names[result] != "garbage":
                self.mqtt_server.addGesture(self.gest_names[result],self.designated_reciever)


    def run(self):
        #threading.Timer(self.sample_period, self.sample).start()
        while(True):
           self.sample()

if __name__ == "__main__":
    include_labels = [0, 1]
    window_length = 100
    overlap = 50
    sample_period = 1/window_length
    weights_file = "../../../data/gesture/classifier_coeffs/left_swipe_classifier_coeffs.csv"
    bias_file = "../../../data/gesture/classifier_coeffs/left_swipe_classifier_bias.csv"
    user = "tommy"
    gestures = ["left_swipe", "garbage"]
    runner = IMUSampleObject(len(include_labels),window_length,overlap, sample_period,weights_file,bias_file, user, gestures)
    runner.run()