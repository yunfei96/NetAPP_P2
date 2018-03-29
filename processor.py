import rmq_params as p
import pika
import argparse
import pickle
import sys
def parse():
    parser = argparse.ArgumentParser(description='Arguments for client.')
    parser.add_argument('-s', dest='server_ip',  help="server ip", type = str, action="store", default="192.168.0.101")
    args = parser.parse_args()
    return args.server_ip

def connect_rbmq(server_ip):
    #-----------connect to rabbitmq server-------------
    credentials = pika.PlainCredentials(p.rmq_params["username"], p.rmq_params["password"])
    parameters = pika.ConnectionParameters(server_ip, 5672, p.rmq_params["vhost"], credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    print("[Checkpoint] Connected to vhost %s on RMQ server at localhost as user %s" %(p.rmq_params["vhost"],p.rmq_params["username"]))
    return channel

def rbq_send(channel,device,message):
    channel.basic_publish(exchange=p.rmq_params["exchange"],
                          routing_key=device,
                          body=message)

def callback(ch, method, properties, body):
    receipt = pickle.loads(body)
    print("[Checkpoint] Consuming from RMQ queue: order-Q")
    #start order
    print("Starting order: %i" %receipt[0])
    rbq_send(ch,"client",pickle.dumps(2))
    #====== started status to LED
    rbq_send(channel,"led",pickle.dumps('st'))
    #====== end of LED
    #finish order
    print("Completed order: %i" %receipt[0])
    rbq_send(ch,"client",pickle.dumps(3))
    #====== finished status to LED
    rbq_send(channel,"led",pickle.dumps('f'))
    #====== end of LED

server_ip = parse()
channel = connect_rbmq(server_ip)
channel.basic_consume(callback,
                      queue=p.rmq_params["order_queue"],
                      no_ack=True)

channel.start_consuming()
