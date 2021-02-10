import sys

PATH = [
    "src/comms/mqtt"
]

for lib in PATH:
    sys.path.append(lib)

import mqtt

# defining for test script
if __name__ == '__main__':
    # Test Rx
    mqtt_rx = mqtt.MQTTLink("ece180d/MEAT")
    mqtt_rx.listen()
