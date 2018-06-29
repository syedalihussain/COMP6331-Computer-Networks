# -*- coding: utf-8 -*-
"""
Created on Sat May 19 15:56:47 2018

@author: Syed Ali Hussain
"""

import paho.mqtt.client as mqtt
import logging
import time
import numpy as np
import matplotlib.pyplot as plt

def on_log(client, userdata, level, buf):
    '''The callback function that is called when client receives an on_log'''
    logging.info(buf)
def on_connect(client, userdata, flags, rc):
    '''The callback function that is called when the client tries to connect
        with the broker'''
    if rc == 0:
        logging.info("Connected OK")
    else:
        logging.info("Bad connection. Returned code: ", str(rc))
    
    
def on_message(client, userdata, msg):
    '''The callback function that is called when client receives a message from 
        the broker'''
    global counters, start_values, start_fresh, last_values, msgs_lost, msgs_duplicate, msgs_unordered
    global dropped_array, received_array, sent_array, connected_array, heap_array
    
    broker_list = ["$SYS/broker/load/publish/dropped/1min", "$SYS/broker/load/publish/received/1min", "$SYS/broker/load/publish/sent/1min", 
                   "$SYS/broker/heap/current", "$SYS/broker/clients/connected"]
    
    #   Checking if the message received is a SYS topic and then updating
    #   different variables and printing it
    if msg.topic in broker_list:
        index = broker_list.index(msg.topic)
        string = str(msg.payload)[2:-1]
        if index == 0:
            dropped_array.append([int(float(string))])
        elif index == 1:
            received_array.append([int(float(string))])
        elif index == 2:
            sent_array.append([int(float(string))])
        elif index == 3:
            heap_array.append([int(float(string))])
        elif index == 4:
            connected_array.append([int(float(string))])
        print(msg.topic + " " + str(msg.payload))
    
    #   Getting the counter number and its count
    counter_str = msg.topic[-2:]
    counter_number = str(msg.payload)[2:-1]
    
    #   Updating messages received dropped, lost and unordered for each of the
    #   counters q0, q1 and q2
    if counter_number.isdigit():
        counter_int = int(counter_number)
        if counter_str == 'q0':
            if counter_int < last_values[0]:
                msgs_unordered[0] += 1
            if msg.dup:
                msgs_duplicate[0] += 1
            if start_fresh[0]:
                start_values[0] = counter_int
                start_fresh[0] = False
            counters[0] += 1
            last_values[0] = counter_int
        elif counter_str == 'q1':
            if counter_int < last_values[1]:
                msgs_unordered[1] += 1
            if msg.dup:
                msgs_duplicate[1] += 1
            if start_fresh[1]:
                start_values[1] = counter_int
                start_fresh[1] = False
            counters[1] += 1
            last_values[1] = counter_int
        elif counter_str == 'q2':
            if counter_int < last_values[2]:
                msgs_unordered[2] += 1
            if msg.dup:
                msgs_duplicate[2] += 1
            if start_fresh[2]:
                start_values[2] = counter_int
                start_fresh[2] = False
            counters[2] += 1
            last_values[2] = counter_int
            
    
def on_publish(client, userdata, mid):
    print("Message published with message id: ",mid)

#   Initialing variables for different statistics
counters, start_values, last_values, msgs_lost, msgs_duplicate, msgs_unordered = np.zeros((6, 3), dtype=int)
start_fresh = np.array([True, True, True])
dropped_array, received_array, sent_array, connected_array, heap_array = ([] for i in range(5))
dropped, received, sent, connected, heap = ([] for i in range(5))
received_c, lost, duplicated, outoforder = ([] for i in range(4))
client_values = []


client = mqtt.Client(client_id='3310-u6028474', clean_session=True, userdata=None)
client.on_log = on_log
client.on_connect = on_connect
client.on_message = on_message
client.on_publish = on_publish
client.username_pw_set(username='3310student', password='comp3310')
client.connect("3310exp.hopto.org")
client.loop_start()

#   Subscribing to all the topics
client.subscribe("$SYS/broker/load/publish/+/1min")
client.subscribe("$SYS/broker/heap/current")
client.subscribe("$SYS/broker/clients/connected")
file = open("reporting_statistics.txt", "a")
print("The program will print out all the SYS calls but not the counter values.")
print("Default it is configured to run for 2 minutes for each of the QoS.")
print("At the end of 1 minute, statistics will be printed out. So stay put ! ! !")
for i in range(0,3):
    print("QoS level: ", i)
    #   Subscribing to all counter with varying QoS
    client.subscribe([("counter/fast/q0", i), ("counter/fast/q1", i), ("counter/fast/q2", i)])
    #   Wait for 10 minutes before calculating avergae
    for j in range(2):
        time.sleep(60)
        
        #   GETTING STATISTICS
        #   Calculating the number of messages received per minute
        rate_msgs_recv = round((np.max(counters) / 1.), 2)
        #   Calculating the rate of messages lost
        argmax = np.argmax(last_values - start_values - counters + 1)
        total_messages = (last_values-start_values)[argmax]
        rate_msgs_lost = round(((np.max(last_values - start_values - counters + 1) / 1. ) / total_messages), 5)
        #   Calculating the rate of messages duplicated
        argmax = np.argmax(msgs_duplicate)
        total_messages = (last_values-start_values)[argmax]
        rate_msgs_duplicate = round(((np.max(msgs_duplicate) / 1.) / total_messages), 5)
        #   Calculating the rate of unordered messages
        argmax = np.argmax(msgs_unordered)
        total_messages = (last_values-start_values)[argmax]
        rate_msgs_unordered = round(((np.max(msgs_unordered) / 1.) / total_messages), 5)
        
        #   Publishing the results to the broker
        print("Publishing the results to the broker now for QoS: ", i)
        print("Number of messages received: ", rate_msgs_recv)
        print("Rate of messages lost", rate_msgs_lost)
        print("Rate of messages duplicated", rate_msgs_duplicate)
        print("Rate of messages out of order", rate_msgs_unordered)
        publish_list = [(rate_msgs_recv, "/recv"), (rate_msgs_lost, "/loss"), 
                        (rate_msgs_duplicate, "/dupe"), (rate_msgs_unordered, "/ooo")]
        if j == 1:
            for rate, j in publish_list:
                topic = "studentreport/u6028474/" + str(int(time.time())) + "/" + str(i) + j
                client_values.append(int(rate))
                message = str(rate)
                client.publish(topic=topic, payload=message, qos=2, retain=True)
                file.write(topic + " " + message + "\n")
        #   Updating the dropped, received, sent message arrays, connected number
        #   of connected clients and current size of heap
        dropped.append([np.mean(dropped_array)])
        received.append([np.mean(received_array)])
        sent.append([np.mean(sent_array)])
        connected.append([np.mean(connected_array)])
        heap.append([np.mean(heap_array)])
        received_c.append([rate_msgs_recv])
        lost.append([rate_msgs_lost])
        duplicated.append([rate_msgs_duplicate])
        outoforder.append([rate_msgs_unordered])
        #   Resetting the arrays for new QoS
        counters, start_values, last_values, msgs_lost, msgs_duplicate, msgs_unordered = np.zeros((6, 3), dtype=int)
        start_fresh = np.array([True, True, True])
        dropped_array, received_array, sent_array, connected_array, heap_array = ([] for i in range(5))
    
    client.unsubscribe([("counter/fast/q0"), ("counter/fast/q1"), ("counter/fast/q2")])
    time.sleep(5)

time.sleep(6)
client.loop_stop()
client.disconnect()
file.close()
print(time.time())


f = plt.figure(figsize=(20,10))
ax0 = f.add_subplot(241)
ax0.plot([x for x in range(len(dropped))], dropped, linestyle='solid')
plt.title('Load Dropped')
ax1 = f.add_subplot(242)
ax1.plot([x for x in range(len(received))], received, c='blue')
plt.title('Load Received')
ax2 = f.add_subplot(243)
ax2.plot([x for x in range(len(sent))], sent, c='red')
plt.title('Load Sent')
ax3 = f.add_subplot(244)
ax3.plot([x for x in range(len(connected))], connected, c='blue')
plt.title('Load Connected')
ax4 = f.add_subplot(245)
ax4.plot([x for x in range(len(heap))], heap, c='red')
plt.title('Heap')
ax5 = f.add_subplot(246)
ax5.plot([x for x in range(len(lost))], lost, c='blue')
plt.title('Client Lost')
ax6 = f.add_subplot(247)
ax6.plot([x for x in range(len(duplicated))], duplicated, c='red')
plt.title('Client Duplicated')
ax7 = f.add_subplot(248)
ax7.plot([x for x in range(len(outoforder))], outoforder, c='blue')
plt.title('Client Out-of-order')

plt.show()
