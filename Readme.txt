Yunfei Guo
yunfei96@vt.edu
Worked on server.py and client.py

Theo Long
2333@vt.edu
Worked on proceesor.py and led.py

Unusual situation:
	We discovered that because of auto_delete=True in rbmq, led.py and processor.py will not be able to connect to server because of auto-deleted queue. For example, if led.py is terminated manually, led_q will be deleted from the server. led.py will not be able to connect to the queue unless having server restarted (re-construct the queue). We tried to handle this problem, but fail to do so because of auto-delete setting.


