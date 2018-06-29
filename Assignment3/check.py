# -*- coding: utf-8 -*-
"""
Created on Sat May 19 15:56:47 2018

@author: hussa
"""

import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import logging
import time
import datetime
def on_log(client, userdata, level, buf):
    logging.info(buf)
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("Connected OK")
    else:
        logging.info("Bad connection. Returned code: ", str(rc))
    
    
def on_message(client, userdata, msg):
    
    #print(msg.topic + " " + str(msg.payload))
    global file
    file.write(msg.topic + " " + str(msg.payload) + "\n")
   # print("Time from start to now is: ", int(now-start))
    
def on_publish(client, userdata, mid):
    print("In on_pub callback mid= ",mid)

file = open("recv.txt", "a")
file.write(str(datetime.datetime.now())[:-7] + "\n")
auth = {'username': '3310student', 'password': 'comp3310'}
client = mqtt.Client(client_id='3310-u6028474', clean_session=True, userdata=None)
client.on_log = on_log
client.on_connect = on_connect
client.on_message = on_message
client.on_publish = on_publish
client.username_pw_set(username='3310student', password='comp3310')
client.connect("3310exp.hopto.org")


client.loop_start()
print(int(time.time()))
# u5809912
#client.subscribe("studentreport/u6028474/#")
#client.subscribe("$SYS/broker/load/publish/+/1min")
client.subscribe("studentreport/#")
#client.subscribe("$SYS/broker/clients/connected")
time.sleep(10)
client.loop_stop()
client.disconnect()
file.close()