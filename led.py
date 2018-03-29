# -*- coding: utf-8 -*-
# @Author: TheoLong
# @Date:   2018-03-29 13:02:41
# @Last Modified by:   TheoLong
# @Last Modified time: 2018-03-29 14:07:14
import RPi.GPIO as GPIO
import rmq_params as p
import pika
import argparse
import pickle
GPIO.setmode(GPIO.BOARD)
#======== here to change pin number  =============
RED = 24
GREEN = 26
BLUE = 28
#=================  preperation  ===============
chan_list = [RED,2GREEN6,BLUE]  # in the order of RGB
GPIO.setup(chan_list, GPIO.OUT) # set to output
def parse():
    parser = argparse.ArgumentParser(description='Arguments for LED.py.')
    parser.add_argument('-s', dest='server_ip',  help="server ip", type = str, action="store", default="192.168.0.101")
    args = parser.parse_args()
    return args.server_ip

'''
==================  status led  ====================
'''
def connected(duration):
    #show blue
    clearAllColor()
    litRGB(0,0,1,duration)
    print('[Checkpoint] Flashing LED to blue')

def disconnected(duration):
    #show red
    clearAllColor()
    litRGB(1,0,0,duration)
    print('[Checkpoint] Flashing LED to red')

def submitted(duration):
    #show purple
    litRGB(1,0,1,duration)
    print('[Checkpoint] Flashing LED to purple')


def started(duration):
    #show yellow
    litRGB(1,1,0,duration)
    print('[Checkpoint] Flashing LED to yellow')

def finished(duration):
    #show green
    litRGB(0,1,0,duration)
    print('[Checkpoint] Flashing LED to green')

'''
==================  indivisual color  ====================
'''
def litRGB(R,G,B,Duration):
    #clear previous color
    clearAllColor()
    onList = []
    if (R > 0):
        onList.append(RED)
    if (G > 0):
        onlist.append(GREEN)
    if (B > 0):
        onlist.append(BLUE)

    if (duration > 0): # unlimited time if duration = 0
        GPIO.output(onList, GPIO.HIGH) 
        sleep(duration)
        clearAllColor()
    else:
        GPIO.output(onList, GPIO.HIGH) 

def clearAllColor():
    GPIO.output(chan_list, GPIO.LOW) 
    #reset all color
'''
==================  rabbit mq  ====================
'''
def connect_rbmq(server_ip):
    #-----------connect to rabbitmq server-------------
    credentials = pika.PlainCredentials(p.rmq_params["username"], p.rmq_params["password"])
    parameters = pika.ConnectionParameters(server_ip, 5672, p.rmq_params["vhost"], credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    print("[Checkpoint] Connected to vhost %s on RMQ server at %s as user %s" %(p.rmq_params["vhost"],server_ip, p.rmq_params["username"]))
    return channel

def callback(ch, method, properties, body):
    receipt = pickle.loads(body)
    print("[Checkpoint] Consuming from RMQ queue: led-Q")
    #flash LED
    status = pickle.loads(body)
    if (status == 'c'):
        connected()
    if (status == 'd'):
        disconnected()
    if (status == 'sub'):
        submitted()
    if (status == 'st'):
        started()
    if (status == 'f'):
        finished()   

#================   main    =========================
server_ip = parse()
channel = connect_rbmq(server_ip)
channel.basic_consume(callback,
                      queue=p.rmq_params["led_queue"],
                      no_ack=True)

channel.start_consuming()
GPIO.cleanup()

