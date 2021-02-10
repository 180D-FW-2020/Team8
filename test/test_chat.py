import sys

PATH = [
    "src/comms/mqtt",
    "src/gui",
    "data/gui"
]

for lib in PATH:
    sys.path.append(lib)

import chat
import mqtt
import cv2 as cv
import time

if __name__ == '__main__':
    link = mqtt.MQTTLink(topic='ece180d/MEAT/general')

    manager = chat.BoardManager('Nico')

    message = {
        'message_type'  :   'text',
        'sender'    :   'Nico', 
        'color'     :   (255, 0, 0), 
        'data'      :   'This is a second test message.',
        'time'      :    {
            'hour': 11,
            'minute': 52,
            'second': 0
            },
        'color' :   (255, 255, 255),
        'emoji' :   []
        }

    link.send(message)


    
    

    
    