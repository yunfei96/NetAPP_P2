from bluetooth import *
import argparse
import pickle
import pika
import rmq_params as p
def print_menu(menu):
    for food in menu:
        print (food, end='')
        print (':')
        print ('  price: ', end='')
        print (menu[food]['price'])
        print ('  time: ', end='')
        print (menu[food]['time'])
def order_menu(menu):
    list = str.split(input("Enter food seprate by space: "))
    order = {}
    for item in list:
        order[item] = menu[item]
    return order

def parse():
    parser = argparse.ArgumentParser(description='Arguments for client.')
    parser.add_argument('-s', dest='server_ip',  help="server ip", type = str, action="store", default="192.168.0.101")
    parser.add_argument('-b', dest='bt_ip', help="bt ip", type = str, action="store", default="B8:27:EB:E1:12:00")
    args = parser.parse_args()
    return args.server_ip, args.bt_ip

def connect_rbmq(server_ip):
    #-----------connect to rabbitmq server-------------
    credentials = pika.PlainCredentials(p.rmq_params["username"], p.rmq_params["password"])
    parameters = pika.ConnectionParameters(server_ip, 5672, p.rmq_params["vhost"], credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    print("[Checkpoint] Connected to vhost %s on RMQ server at %s as user %s",p.rmq_params["vhost"],'localhost',p.rmq_params["username"])

#----------connect BT server-----------
(server_addr,bd_addr) = parse()
connect_rbmq(server_addr)
port = 1
sock=BluetoothSocket( RFCOMM )
print (bd_addr)
sock.connect((bd_addr, port))
#receive menu
#sock.send("hello!!")
data = sock.recv(1024)
print(data)
#send order list
#receive receipt
#listen to status queue
sock.close()

