import sys

PATH = [
    "src/comms/mqtt",
    "src/gui",
    "data/gui"
]

for lib in PATH:
    sys.path.append(lib)

import chat
import mqtt_link as mqtt
import cv2 as cv
import time

if __name__ == '__main__':
    image = cv.imread('C:\\Users\\nrgza\\Documents\\180D\\MEAT\\data\\gui\\chat.jpg')

    link = mqtt.MQTTLink(board='ece180d/MEAT/general', user='User 1')

    link.addText('Test', 'The Butcher Bros')

    manager = chat.BoardManager('Nico')

    link.send()
    
    # message = {
    #     'sender'    :   'Nico', 
    #     'color'     :   (255, 0, 0), 
    #     'data'      :   'This is a test message.',
    #     'time'      :    {
    #         'hour': 11,
    #         'minute': 52,
    #         'second': 0
    #         }
    #     }

    
    

    
    