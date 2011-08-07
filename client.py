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
        # Observers of the class
        self.olist = []
        self.fxnlist = []

        # Message queue
        self.queue = []

        # Initialize threading 
        self.lock = threading.Lock()
        self.stop = threading.Event()
        self.net_thread = threading.Thread(target=self.network_thread)
        self.net_thread.daemon = True # Thread will exit if main thread exits
        self.net_thread.start()

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

    def network_thread(self):
        # Listen for UDP messages from the server
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.bind((Config.host, Config.bcast_port))

        while (not self.stop.is_set()):
            try: 
                message, address = sock.recvfrom(8192)
                print "Got data from", address, ":", message
                self.append(message)

            except (KeyboardInterrupt, SystemExit):
                # Unfortunately, in Python, only the main thread receives SIGINT. This is why we use a special terminate flag
                raise


    def terminate(self):
        print "Terminating network thread."
        self.stop.set()
        self.net_thread.join()
        print "Terminated network thread."

# Quadrotor handles the dictionary processing...
class _Quadrotor:
    def __init__(self):
        self.queue = MessageQueue()
        # Networking
        
    def send(self):
        pass

# Make Quadrotor a singleton
_quadrotor = _Quadrotor()
def Quadrotor(): return _quadrotor

msg_queue = MessageQueue()


class Client:
    def __init__(self):
        self.thread = threading.Thread(target=self.run)
        self.daemon = True
        self.stop = threading.Event()
        self.thread.start()

    def run(self):
        while (not self.stop.is_set()):
            x = msg_queue.pop()
            print x
            time.sleep(1)

    def terminate(self):
        print "Terminating client."
        self.stop.set()
        self.thread.join()
        print "Client terminated."

def sample_client():
    # timer: send x every second
    while 1:
        x = msg_queue.pop()
        print x
        time.sleep(1)
    

if __name__ == "__main__":
    # Begin client.
    client = Client()

    # Infinite loop while quadrotor is running.
    # Note: It is difficult to end python threads gracefully, ESPECIALLY when the threads on blocking on I/O. 
    # Unfortunately, we have to Ctrl-Z when server is not running, but Ctrl-C will work when server is up, thanks to terminate calls. This is because only the main thread receives Ctrl-C

    while 1:
        try:
            dummy = None
        except (KeyboardInterrupt, SystemExit):
            print "Main thread keyboard interrupt"
            msg_queue.terminate()
            client.terminate()
            sys.exit()

        
