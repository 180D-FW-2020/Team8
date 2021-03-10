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
import datetime
import math
import pandas as pd
import numpy as np
import mqtt_net as mqtt

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


class IMUSampleObject:

    def __init__(self,classifier : GestClassifier , window_length: int, overlap :int, sample_freq: int, username :str, debug = False):
        # debug status
        self.debug = debug

        # sampling paramaters
        self.window_length = window_length #number of Samples
        self.length_sample = 14
        self.classifier    = classifier
        self.data    = [None]*self.length_sample*window_length
        self.reading = [None]*self.length_sample*(window_length-overlap)
        self.overlap = overlap
        self.samples_taken = 0
        self.sample_freq = sample_freq
        self.sample_period = 1/sample_freq

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

        # Sensor Reading Values
        self.gyroXangle = 0.0
        self.gyroYangle = 0.0
        self.gyroZangle = 0.0
        self.CFangleX = 0.0
        self.CFangleY = 0.0
        self.CFangleXFiltered = 0.0
        self.CFangleYFiltered = 0.0
        self.kalmanX = 0.0
        self.kalmanY = 0.0
        self.oldXAccRawValue = 0
        self.oldYAccRawValue = 0
        self.oldZAccRawValue = 0

         #Setup the tables for the median filter. Fill them all with '1' so we dont get devide by zero error
        self.acc_medianTable1X = [1] * ACC_MEDIANTABLESIZE
        self.acc_medianTable1Y = [1] * ACC_MEDIANTABLESIZE
        self.acc_medianTable1Z = [1] * ACC_MEDIANTABLESIZE
        self.acc_medianTable2X = [1] * ACC_MEDIANTABLESIZE
        self.acc_medianTable2Y = [1] * ACC_MEDIANTABLESIZE
        self.acc_medianTable2Z = [1] * ACC_MEDIANTABLESIZE

        #timers
        self.a = datetime.datetime.now()
        self.b = datetime.datetime.now()
        self.c = datetime.datetime.now()

    def __update_server(self, action: str):
        if action != "garbage":
            now = datetime.datetime.now()
            msg = {
                    "message_type" : "gesture",
                    "sender" : self.mqtt_server._MQTTLink__user,
                    "reciever" : self.designated_reciever,
                    "data" : action,
                    "time" : {
                        "hour":now.hour,
                        "minute": now.minute,
                        "second": now.second
                    }
                }
            self.mqtt_server.send(msg)
        else:
            self.mqtt_server.send()

    def __get_filtered_values(self):
        #Read the accelerometer and gyroscope
        
        ACCx = IMU.readACCx()
        ACCy = IMU.readACCy()
        ACCz = IMU.readACCz()
        GYRx = IMU.readGYRx()
        GYRy = IMU.readGYRy()
        GYRz = IMU.readGYRz()


        ##Calculate loop Period(LP). How long between Gyro Reads
        self.c = self.a
        self.b = datetime.datetime.now() - self.a
        self.a = datetime.datetime.now()
        LP = self.b.microseconds/(1000000*1.0)
        outputString = "Loop Time %5.2f " % ( LP )

        ###############################################
        #### Apply low pass filter ####
        ###############################################
        ACCx =  ACCx  * ACC_LPF_FACTOR + self.oldXAccRawValue*(1 - ACC_LPF_FACTOR)
        ACCy =  ACCy  * ACC_LPF_FACTOR + self.oldYAccRawValue*(1 - ACC_LPF_FACTOR)
        ACCz =  ACCz  * ACC_LPF_FACTOR + self.oldZAccRawValue*(1 - ACC_LPF_FACTOR)

        self.oldXAccRawValue = ACCx
        self.oldYAccRawValue = ACCy
        self.oldZAccRawValue = ACCz

        #########################################
        #### Median filter for accelerometer ####
        #########################################
        # cycle the table
        for x in range (ACC_MEDIANTABLESIZE-1,0,-1 ):
            self.acc_medianTable1X[x] = self.acc_medianTable1X[x-1]
            self.acc_medianTable1Y[x] = self.acc_medianTable1Y[x-1]
            self.acc_medianTable1Z[x] = self.acc_medianTable1Z[x-1]

        # Insert the lates values
        self.acc_medianTable1X[0] = ACCx
        self.acc_medianTable1Y[0] = ACCy
        self.acc_medianTable1Z[0] = ACCz

        # Copy the tables
        self.acc_medianTable2X = self.acc_medianTable1X[:]
        self.acc_medianTable2Y = self.acc_medianTable1Y[:]
        self.acc_medianTable2Z = self.acc_medianTable1Z[:]

        # Sort table 2
        self.acc_medianTable2X.sort()
        self.acc_medianTable2Y.sort()
        self.acc_medianTable2Z.sort()

        # The middle value is the value we are interested in
        ACCx = self.acc_medianTable2X[int(ACC_MEDIANTABLESIZE/2)]
        ACCy = self.acc_medianTable2Y[int(ACC_MEDIANTABLESIZE/2)]
        ACCz = self.acc_medianTable2Z[int(ACC_MEDIANTABLESIZE/2)]

        #Convert Gyro raw to degrees per second
        rate_gyr_x =  GYRx * G_GAIN
        rate_gyr_y =  GYRy * G_GAIN
        rate_gyr_z =  GYRz * G_GAIN

        #Calculate the angles from the gyro.
        self.gyroXangle+=rate_gyr_x*LP
        self.gyroYangle+=rate_gyr_y*LP
        self.gyroZangle+=rate_gyr_z*LP

        #Convert Accelerometer values to degrees
        AccXangle =  (math.atan2(ACCy,ACCz)*RAD_TO_DEG)
        AccYangle =  (math.atan2(ACCz,ACCx)+M_PI)*RAD_TO_DEG


        #Change the rotation value of the accelerometer to -/+ 180 and
        #move the Y axis '0' point to up.  This makes it easier to read.
        if AccYangle > 90:
            AccYangle -= 270.0
        else:
            AccYangle += 90.0

        #Complementary filter used to combine the accelerometer and gyro values.
        self.CFangleX=AA*(self.CFangleX+rate_gyr_x*LP) +(1 - AA) * AccXangle
        self.CFangleY=AA*(self.CFangleY+rate_gyr_y*LP) +(1 - AA) * AccYangle

        #Kalman filter used to combine the accelerometer and gyro values.
        self.kalmanY = kalmanFilterY(AccYangle, rate_gyr_y,LP)
        self.kalmanX = kalmanFilterX(AccXangle, rate_gyr_x,LP)

        #Normalize accelerometer raw values.
        accXnorm = ACCx/math.sqrt(ACCx * ACCx + ACCy * ACCy + ACCz * ACCz)
        accYnorm = ACCy/math.sqrt(ACCx * ACCx + ACCy * ACCy + ACCz * ACCz)

        #Calculate pitch and roll
        pitch = math.asin(accXnorm)
        roll = -math.asin(accYnorm/math.cos(pitch))


        #        if 1:                       #Change to '0' to stop showing the angles from the accelerometer
        #            outputString += "#  ACCX Angle %5.2f ACCY Angle %5.2f  #  " % (AccXangle, AccYangle)
        #
        #        if 1:                       #Change to '0' to stop  showing the angles from the gyro
        #            outputString +="\t# GRYX Angle %5.2f  GYRY Angle %5.2f  GYRZ Angle %5.2f # " % (self.gyroXangle,self.gyroYangle,self.gyroZangle)
        #
        #        if 1:                       #Change to '0' to stop  showing the angles from the complementary filter
        #            outputString +="\t#  CFangleX Angle %5.2f   CFangleY Angle %5.2f  #" % (self.CFangleX,self.CFangleY)
        #
        #
        #        if 1:                       #Change to '0' to stop  showing the angles from the Kalman filter
        #            outputString +="# kalmanX %5.2f   kalmanY %5.2f #" % (self.kalmanX,self.kalmanY)


        # Enforce sampling period--maybe do this outside of this function
        time_remaining = self.sample_period - ((datetime.datetime.now()-self.c).microseconds)/(1000000*1.0)
        #print(time_remaining)
        if(time_remaining <0):
            time_remaining = 0
        time.sleep(time_remaining)
        return [AccXangle, AccYangle,self.gyroXangle,self.gyroYangle,self.gyroZangle,self.CFangleX,self.CFangleY,self.kalmanX,self.kalmanY, pitch, roll,ACCx,ACCy,ACCz]

    def sample(self):

        # filtered sample
        sample = self.__get_filtered_values()

        for i in range(self.length_sample):
            self.reading[self.samples_taken*self.length_sample + i] = sample[i]
        
        self.samples_taken += 1

        if not(self.samples_taken % (self.window_length-self.overlap)):
            self.data = np.roll(self.data, (self.window_length - self.overlap)*self.length_sample)
            self.data[self.length_sample*(self.window_length-self.overlap):] = self.reading
            self.samples_taken = 0
            result = self.classifier.classify_action(self.data)

            # apply result to mqtt link
            self.__update_server(result)

    def run(self):
        self.a = datetime.datetime.now()
        while True:
           self.sample()

    def create_database(self, number_of_readings :int, data_frame = None):
        data = pd.DataFrame()
        if data_frame:
            data = data_frame

        for label, gesture in enumerate(self.classifier.gest_dict):
            print("Generating " + self.classifier.gest_dict[label] + " database:")
            for reading in range(number_of_readings):
                print("Reading " + str(reading) + "...")
                for each_sample in range(self.window_length):

                    sample = self.__get_filtered_values()
        
                    for i in range(self.length_sample):
                        self.data[each_sample*self.length_sample + i] = sample[i]

                labeled_data = np.insert(self.data,0, label)
                df = pd.DataFrame([labeled_data], columns=np.arange(self.window_length*self.length_sample+1))
                data = data.append(df, ignore_index=True)
                print("Finished reading sample " + str(reading))
                time.sleep(1)
                # timer reset
                self.a = datetime.datetime.now()
                self.b = datetime.datetime.now()
                self.c = datetime.datetime.now()
        return data


        
def kalmanFilterY ( accAngle, gyroRate, DT):
    y=0.0
    S=0.0

    global KFangleY
    global Q_angle
    global Q_gyro
    global y_bias
    global YP_00
    global YP_01
    global YP_10
    global YP_11

    KFangleY = KFangleY + DT * (gyroRate - y_bias)

    YP_00 = YP_00 + ( - DT * (YP_10 + YP_01) + Q_angle * DT )
    YP_01 = YP_01 + ( - DT * YP_11 )
    YP_10 = YP_10 + ( - DT * YP_11 )
    YP_11 = YP_11 + ( + Q_gyro * DT )

    y = accAngle - KFangleY
    S = YP_00 + R_angle
    K_0 = YP_00 / S
    K_1 = YP_10 / S

    KFangleY = KFangleY + ( K_0 * y )
    y_bias = y_bias + ( K_1 * y )

    YP_00 = YP_00 - ( K_0 * YP_00 )
    YP_01 = YP_01 - ( K_0 * YP_01 )
    YP_10 = YP_10 - ( K_1 * YP_00 )
    YP_11 = YP_11 - ( K_1 * YP_01 )

    return KFangleY

def kalmanFilterX ( accAngle, gyroRate, DT):
    x=0.0
    S=0.0

    global KFangleX
    global Q_angle
    global Q_gyro
    global x_bias
    global XP_00
    global XP_01
    global XP_10
    global XP_11


    KFangleX = KFangleX + DT * (gyroRate - x_bias)

    XP_00 = XP_00 + ( - DT * (XP_10 + XP_01) + Q_angle * DT )
    XP_01 = XP_01 + ( - DT * XP_11 )
    XP_10 = XP_10 + ( - DT * XP_11 )
    XP_11 = XP_11 + ( + Q_gyro * DT )

    x = accAngle - KFangleX
    S = XP_00 + R_angle
    K_0 = XP_00 / S
    K_1 = XP_10 / S

    KFangleX = KFangleX + ( K_0 * x )
    x_bias = x_bias + ( K_1 * x )

    XP_00 = XP_00 - ( K_0 * XP_00 )
    XP_01 = XP_01 - ( K_0 * XP_01 )
    XP_10 = XP_10 - ( K_1 * XP_00 )
    XP_11 = XP_11 - ( K_1 * XP_01 )

    return KFangleX

if __name__ == "__main__":
    include_labels = [0, 1]
    window_length = 50
    overlap = 25
    sample_freq = 30
    sample_size = 14
    weights_file = "../../../data/gesture/classifier_coeffs/ls_classifier_coeffs.csv"
    bias_file =    "../../../data/gesture/classifier_coeffs/ls_classifier_bias.csv"
    user = "tommy_rpi"
    gestures = ["left_swipe", "garbage"]
    left_swipe_classifier = GestClassifier(len(gestures),sample_size*window_length,weights_file,bias_file,include_labels,gestures )
    runner = IMUSampleObject(left_swipe_classifier,window_length,overlap,sample_freq,user)
    runner.run()
