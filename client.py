#!/usr/bin/env python

import socket
import serial
import threading
from config import Config
import time
import sys

# Thread-safe message queue
# Also uses the observer pattern to update listeners, but you can also just call pop to return the newest element. If there is more than one person listening in, you might want to implement something other than "pop" that doesn't remove the last element but simply returns it...
class MessageQueue:
    def __init__(self):
        self.lock = threading.Lock()

        # Observers of the class
        self.olist = []
        self.fxnlist = []

        # Message queue
        self.queue = []
        pass

    def register(self, observer):
        self.olist.append(observer)
    
    def register_callback(self, callback):
        self.fxnlist.append(callback)

    def pop(self):
        x = None
        self.lock.acquire()
        if len(self.queue) != 0:
            x = self.queue.pop()
        self.lock.release()
        return x

    def append(self, x):
        self.lock.acquire()
        self.queue.append(x)
        # Check if we have saturated the max number of messages in the queue
        if len(self.queue) > Config.max_queue_len:
            del self.queue[0]
        self.lock.release()

        # Update all classes that might be listening in
        for o in self.olist:
            o.notify()
        # Execute all callbacks
        for f in self.fxnlist:
            f()
        pass

class Quadcopter:
    def __init__(self):
        self.queue = MessageQueue()
        # Networking
        
    def send(self):
        pass


msg_queue = MessageQueue()

def network_thread():
    # Listen for UDP messages from the server
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind((Config.host, Config.bcast_port))

    while 1:
        try: 
            message, address = sock.recvfrom(8192)
            print "Got data from", address, ":", message
            msg_queue.append(message)

        except (KeyboardInterrupt, SystemExit):
            raise
#        except:
#            traceback.print_exc()


def sample_client():
    # timer: send x every second
    while 1:
        x = msg_queue.pop()
        print x
        time.sleep(1)
    

if __name__ == "__main__":
    # Begin threads
    threading.Thread(target=network_thread).start()
    threading.Thread(target=sample_client).start()

    # Infinite loop while quadrotor is running
    while 1:
        pass

        
