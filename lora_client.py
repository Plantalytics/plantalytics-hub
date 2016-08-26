#!/usr/bin/python

import paho.mqtt.client as mqtt
import time

# Connect to the right channel
def on_connect(client, userdata, rc):
    print("Connected with result code "+str(rc))
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
    client.subscribe("lora/+/+")

# The callback for when a PUBLISH message is recieved
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    myfile = open("data_stream.txt", "a")
    myfile.write(msg.topic+" "+str(msg.payload))
    myfile.write(str(int(time.time()*1000))+'\n')
    myfile.write('\n')
    myfile.close()

#clear txt file
open("data_stream.txt", "a").close()
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# client.connect("iot.eclipse.org", 1883, 60)
client.connect("localhost")

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
