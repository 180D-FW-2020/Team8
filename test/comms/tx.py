import mqtt_net as mqtt

# defining for test script
if __name__ == '__main__':

    # Note: make sure you are reading values from a subscriber on the same board to see the result
    # Start a client
    mqtt_tx = mqtt.MQTTLink("ece180d/MEAT/general", user_id = 'Jack')

    message = {
        'sender'    :   'Jack', 
        'color'     :   (255, 0, 0), 
        'data'      :   'This is a test message.',
        'time'      :    {
            'hour': 11,
            'minute': 52,
            'second': 0
        },
        'emoji' : [1, 5]
    }

    mqtt_tx.send(message)