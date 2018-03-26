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
    return server_sock

order_ID = 0
#-----------------main start here----------------
while 1:
    server_sock=start_BTS()
    print("[Checkpoint] Waiting for connection on RFCOMM channel 1")
    client_sock, client_info = server_sock.accept()
    print("[Checkpoint] Accepted connection from " %client_info)
    try:
        #-------send menu-------
        raw_menu = menu.menu
        send_menu = pickle.dumps(raw_menu)
        client_sock.send(raw_menu)
        print("[Checkpoint] Sent menu:")
        print_menu()
        #-------receive order----
        data = client_sock.recv(1024)
        order_list = pickle.loads(data)
        print("[Checkpoint] Received order:")
        print(order_list)
        #-------proccess order----
        price =0
        time =0
        re = []
        for item in order_list:
            if item in menu.menu.keys():
                price = price + menu.menu[item]['price']
                time = time + menu.menu[item]['time']
                re.append(item)
        #-------send back---------
        print("[Checkpoint] Sent receipt:")
        print("Order ID: ", end='')
        print(i)
        print("Items: ", end='')
        print(re)
        print("Total Price: ",end='')
        print(price)
        print("Total Time: ",end='')
        print(time)
        receipt = pickle.dumps((i,re,price,time))
        client_sock.send(receipt)
        print("[Checkpoint] Closed Bluetooth Connection.")
        client_sock.close()
    except IOError:
            pass
    i=i+1
server_sock.close()
