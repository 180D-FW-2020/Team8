import cv2 as cv
import paho.mqtt.client as mqtt

class ARChat():
    def __init__(self):
        self.messages = []
    
    def queue(self, user, message, color, timestamp):
        self.messages.insert(0, (user, message, color, timestamp))
        print(self.messages)

    def write(self, im, out):
        index = 0
        for message in self.messages:
            cv.putText(im, "<" + message[3] + "> " + message[0] + ": " + message[1], (20, im.shape[0]-80-50*index), cv.FONT_HERSHEY_SIMPLEX, 1, message[2], 2, cv.LINE_AA)
            index += 1
        cv.imwrite(out, im)


if __name__ == '__main__':
    chat = ARChat()

    def on_connect(client, userdata, flags, rc):
        print("Connection returned result: " + str(rc))
        client.subscribe("ece180d/chatar", qos=1)

    def on_disconnect(client, userdata, rc):
        if rc != 0:
            print('Unexpected Disconnect')
        else:
            print('Expected Disconnect')

    def on_message(client, userdata, message):
        print(str(message.payload))
        chat.queue(str(userdata), str(message.payload), (255,255,0), '12:46')
        chat.write(cv.imread('img.jpg', 1), 'img_edited.jpg')

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.connect_async('mqtt.eclipseprojects.io')
    client.loop_start()
    while True:
        pass
    client.loop_stop()
    client.disconnect()