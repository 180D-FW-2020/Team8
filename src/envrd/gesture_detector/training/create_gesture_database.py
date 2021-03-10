##
 #  File: create_gesture_database.py
 # 
 #  Author: Thomas Kost
 #  
 #  Date: 15 November 2020
 #  
 #  @brief create database for gestures, script makes user friendly way to generate gesture dataset
 #
import RPi.GPIO as GPIO
import sys
import IMU
import time
import pandas as pd
import numpy as np
 
# Constants:
RAD_TO_DEG = 57.29578
M_PI = 3.14159265358979323846
G_GAIN = 0.070          # [deg/s/LSB]  If you change the dps for gyro, you need to update this value accordingly
AA =  0.40              # Complementary filter constant
ACC_LPF_FACTOR = 0.4    # Low pass filter constant for accelerometer
ACC_MEDIANTABLESIZE = 9         # Median filter table size for accelerometer. Higher = smoother but a longer delay

#Kalman filter variables
Q_angle = 0.02
Q_gyro = 0.0015
R_angle = 0.005
y_bias = 0.0
x_bias = 0.0
XP_00 = 0.0
XP_01 = 0.0
XP_10 = 0.0
XP_11 = 0.0
YP_00 = 0.0
YP_01 = 0.0
YP_10 = 0.0
YP_11 = 0.0
KFangleX = 0.0
KFangleY = 0.0


#initialize sensor
IMU.detectIMU()
if(IMU.BerryIMUversion == 99):
    print(" No BerryIMU found...sick nasty")
    sys.exit()
IMU.initIMU() # initialize all the relevant sensors

# Hardware Varibles and setup
green_led = 21
red_led = 13
GPIO.setmode(GPIO.BCM)
GPIO.setup(green_led, GPIO.OUT, initial=GPIO.LOW )
GPIO.setup(red_led, GPIO.OUT, initial=GPIO.LOW )

# gestures
gestures = ["left_swipe", "garbage"]

# database params
itterations = 100
duration = 1 # seconds

sample_per_itteration = [None]*itterations

data = pd.DataFrame()

for label,gesture in enumerate(gestures):
    print(gesture)
    time.sleep(1)
    for i in range(itterations):
        time_st = time.time()
        reading = np.array([])
        samples = 0
        # change lights
        GPIO.output(green_led,GPIO.HIGH)
        GPIO.output(red_led,GPIO.LOW)
        while (time.time() -time_st) < duration:
            # read accelerometer
            ACCx = IMU.readACCx()
            ACCy = IMU.readACCy()
            ACCz = IMU.readACCz()
            GYRx = IMU.readGYRx()
            GYRy = IMU.readGYRy()
            GYRz = IMU.readGYRz()
            reading = np.append(reading, ACCx)
            reading = np.append(reading, ACCy)
            reading = np.append(reading, ACCz)
            reading = np.append(reading, GYRx)
            reading = np.append(reading, GYRy)
            reading = np.append(reading, GYRz)

            # may need to introduce some delay to ensure our sampling rate at run time is similar
            # time.sleep(0)
            samples+=1
        # change lights
        GPIO.output(green_led,GPIO.LOW)
        GPIO.output(red_led,GPIO.HIGH)
        
        print(samples)
        time.sleep(duration)
        sample_per_itteration[i] = samples
        reading = np.insert(reading,0, label)
        
        #make column labels
        df = pd.DataFrame([reading], columns=np.arange(samples*6+1))
        data=data.append(df, ignore_index=True)
min_len = min(sample_per_itteration) + 1
max_len = max(sample_per_itteration)+ 1
remove_cols = np.arange(min_len+1,max_len+1)

data = data.drop(columns=remove_cols)

data.to_csv("meat_gesture_database_testing.csv", mode='a', header=False)
GPIO.cleanup()
