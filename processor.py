import rmq_params as p
import pika

def connect_rbmq():
    #-----------connect to rabbitmq server-------------
    credentials = pika.PlainCredentials(p.rmq_params["username"], p.rmq_params["password"])
    parameters = pika.ConnectionParameters('localhost', 5672, p.rmq_params["vhost"], credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    print("[Checkpoint] Connected to vhost %s on RMQ server at localhost as user %s" %(p.rmq_params["vhost"],p.rmq_params["username"]))
    return channel

def callback(ch, method, properties, body):
    print(" [x] %r:%r" % (method.routing_key, body))

channel = connect_rbmq()
channel.basic_consume(callback,
                      queue=p.rmq_params["order_queue"],
                      no_ack=True)

channel.start_consuming()
