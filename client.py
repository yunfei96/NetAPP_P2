from bluetooth import *
import argparse
import pickle
import pika
import sys
import rmq_params as p
enter_time =0
def print_menu(menu):
    for food in menu:
        print (food, end='')
        print (':')
        print ('  price: ', end='')
        print (menu[food]['price'])
        print ('  time: ', end='')
        print (menu[food]['time'])


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
    print("[Checkpoint] Connected to vhost %s on RMQ server at %s as user %s" %(p.rmq_params["vhost"],'localhost',p.rmq_params["username"]))
    return channel

def callback(ch, method, properties, body):
    input = pickle.loads(body)
    global enter_time
    if enter_time == 0:
        print("[Checkpoint] Consuming from RMQ queue: %r" %method.routing_key)
        enter_time = 1
    if(input == 1):
        print("[Checkpoint] Order Update: Your order has been submitted.")
    elif(input == 2):
        print("[Checkpoint] Order Update: We are processing your order.")
    else:
        print("[Checkpoint] Order Update: We finished processing your order.")
        sys.exit()


#----------connect BT server-----------

(server_addr,bd_addr) = parse()
port = 1
sock=BluetoothSocket( RFCOMM )
sock.connect((bd_addr, port))
print ("[Checkpoint] Connected")
#-----receive menu
data = sock.recv(1024)
print("[Checkpoint] Received menu:")
mymenu = pickle.loads(data)
print_menu(mymenu)
list = str.split(input("Enter food seprate by space: "))
#------send order list
print("[Checkpoint] Sent order:")
print(list)
order_list = pickle.dumps(list)
sock.send(order_list)
#-------receive receipt
print("[Checkpoint] Received receipt:")
data = sock.recv(1024)
receipt = pickle.loads(data)
print("Order ID: ",end='')
print(receipt[0])
print("Items: ", end='')
print(receipt[1])
print("Total Price: ",end='')
print(receipt[2])
print("Total Time: ", end='')
print(receipt[3])
print("[Checkpoint] Closed Bluetooth Connection.")
sock.close()
#listen to status queue
channel = connect_rbmq(server_addr)
channel.basic_consume(callback,
                      queue=str(receipt[0]),
                      no_ack=True)

channel.start_consuming()
