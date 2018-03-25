from bluetooth import *
import menu
import rmq_params as p
import pika
import pickle

def print_menu(menu):
    for food in menu:
        print (food, end='')
        print (':')
        print ('  price: ', end='')
        print (menu[food]['price'])
        print ('  time: ', end='')
        print (menu[food]['time'])
def connect_rbmq():
    #-----------connect to rabbitmq server-------------
    credentials = pika.PlainCredentials(p.rmq_params["username"], p.rmq_params["password"])
    parameters = pika.ConnectionParameters('localhost', 5672, p.rmq_params["vhost"], credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    print("[Checkpoint] Connected to vhost %s on RMQ server at %s as user %s",p.rmq_params["vhost"],'localhost',p.rmq_params["username"])
def setup_q_e():
    #----------declare exchange and queue---------------
    channel.exchange_declare(exchange= p.rmq_params["exchange"],
                         exchange_type='direct')
    channel.queue_declare(p.rmq_params["order_queue"], auto_delete=True)
    channel.queue_declare(p.rmq_params["led_queue"], auto_delete=True)
    print("[Checkpoint] Setting up exchanges and queues...")
    '''
    channel.queue_declare(p.rmq_params["exchange"], auto_delete=True)
    channel.basic_publish(exchange='order_system',
    routing_key=severity,
    body=message)
    '''
def start_BTS():
    #start a bluetooth server
    port = 1
    server_sock=BluetoothSocket( RFCOMM )
    print("[Checkpoint] Bluetooth ready!")
    server_sock.bind(("",port))
    server_sock.listen(1)
    print("[Checkpoint] Waiting for connection on RFCOMM channel 1")
    client_sock, client_info = server_sock.accept()
    print("[Checkpoint] Accepted connection from ", client_info)

start_BTS()
try:
    #-------send menu-------
    raw_menu = menu.menu
    send_menu = pickle.dumps(raw_menu)
    client_sock.send('hello')
    print("[Checkpoint] Sent menu:")
    #print_menu()
    #-------receive order----
    #-------proccess order----
    #-------send back---------
    #data = client_sock.recv(1024)
except IOError:
    pass

print("disconnected")
client_sock.close()
server_sock.close()
