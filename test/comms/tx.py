import sys

PATH = [
    "src/comms/mqtt"
]

for lib in PATH:
    sys.path.append(lib)
    
import mqtt

# defining for test script
if __name__ == '__main__':

    # Note: make sure you are reading values from a subscriber on the same board to see the result
    # Start a client
    mqtt_tx = mqtt.MQTTLink("ece180d/MEAT/general")

    message = {
        'sender'    :   'Nico', 
        'color'     :   (255, 0, 0), 
        'data'      :   'This is a test message.',
        'time'      :    {
            'hour': 11,
            'minute': 52,
            'second': 0
        }
    }

    mqtt_tx.send(message)