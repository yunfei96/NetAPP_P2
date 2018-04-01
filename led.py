# -*- coding: utf-8 -*-
# @Author: TheoLong
# @Date:   2018-03-29 13:02:41
# @Last Modified by:   TheoLong
# @Last Modified time: 2018-03-31 21:53:13
import RPi.GPIO as GPIO
import rmq_params as p
import pika
import argparse
import pickle
import time
def parse():
    parser = argparse.ArgumentParser(description='Arguments for LED.py.')
    parser.add_argument('-s', dest='server_ip',  help="server ip", type = str, action="store", default="192.168.0.101")
    parser.add_argument('-m', dest='gpio_mode',  help="gpio mode", type = int, action="store", default=10)
    parser.add_argument('-r', dest='RED',  help="red pin", type = int, action="store", default=36)
    parser.add_argument('-g', dest='GREEN',  help="green pin", type = int, action="store", default=38)
    parser.add_argument('-b', dest='BLUE',  help="blue pin", type = int, action="store", default=40)

    args = parser.parse_args()
    return [args.server_ip, args.gpio_mode, args.RED, args.GREEN, args.BLUE]

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
def litRGB(R,G,B,duration):
    #clear previous color
    clearAllColor()
    onList = []
    if (R > 0):
        onList.append(RED)
    if (G > 0):
        onList.append(GREEN)
    if (B > 0):
        onList.append(BLUE)

    if (duration > 0): # unlimited time if duration = 0
        GPIO.output(onList, GPIO.HIGH) 
        time.sleep(duration)
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
    
    #flash LED
    status = pickle.loads(body)
    if (status == 'c'):
        connected(0.5)
    if (status == 'd'):
        disconnected(0.5)
    if (status == 'sub'):
        submitted(0.5)
    if (status == 'st'):
        started(0.5)
    if (status == 'f'):
        finished(0.5)

#================   main    =========================
settings = parse()
server_ip = settings[0]
if settings[1] == 10:
    GPIO.setmode(GPIO.BOARD)
elif settings[1] == 11:
    GPIO.setmode(GPIO.BCM)
else:
    exit('Error: invalid GPIO mode')
#======== here to change pin number  =============
RED = settings[2]
GREEN = settings[3]
BLUE = settings[4]
#=================  preperation  ===============
chan_list = [RED,GREEN,BLUE]  # in the order of RGB
GPIO.setup(chan_list, GPIO.OUT) # set to output
channel = connect_rbmq(server_ip)
print("[Checkpoint] Consuming from RMQ queue: led-Q")
channel.basic_consume(callback,
                      queue=p.rmq_params["led_queue"],
                      no_ack=True)
try:
    channel.start_consuming()
except:
    print("Error: Queue not found. Please restart server")
GPIO.cleanup()

