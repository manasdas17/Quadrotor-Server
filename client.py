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

    def register_class(self, observer):
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
                # print "Got data from", address, ":", message
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
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.bind((Config.host, Config.recv_port))        

    def send(self, dictionary):
        # Accepts a dictionary, parses into string
        string = ""
        for key in dictionary:
            string += str(key) + " " + str(dictionary[key]) + " "
        string += "\n"

        # This doesn't have to be broadcast: change it to send to one computer...
        self.sock.sendto(string, ('<broadcast>', Config.recv_port))

    def pop(self):
        # Return a dictionary of values:
        msg = self.queue.pop()
        d = {}
        if msg != None:
            msg = msg.split()
            # ['a','b','c','d'] -> {'a':'b', 'c':'d'}
            for i in range(len(msg)):
                if (i % 2) == 0:
                    d[str(msg[i])] = int(msg[i+1])
        return d

    def register_callback(self, callback):
        self.queue.register_callback(callback)

    def terminate(self):
        self.queue.terminate()

# Make Quadrotor a singleton
_quadrotor = _Quadrotor()
def Quadrotor(): return _quadrotor

class Client:
    def __init__(self):
        # Set up quadrotor
        self.qrotor = Quadrotor()
        self.qrotor.register_callback(self.callback)

        # Set up threading
        self.thread = threading.Thread(target=self.run)
        self.daemon = True
        self.stop = threading.Event()
        self.thread.start()

    def callback(self):
        print "Msg received!"

    def run(self):
        counter = 0
        # Pop the top serial message from the quadrotor, wait one second, write the same message back, then wait another second.
        while (not self.stop.is_set()):
            x = self.qrotor.pop()
            print "Received: ", x
            time.sleep(1)
            self.qrotor.send(x)
            time.sleep(1)
            counter += 1

    def terminate(self):
        print "Terminating client."
        self.stop.set()
        self.thread.join()
        print "Client terminated."

def main_loop(client):
    while 1:
        try:
            dummy = None
        except (KeyboardInterrupt, SystemExit):
            print "Main thread keyboard interrupt"
            Quadrotor().terminate()
            client.terminate()
            sys.exit()

if __name__ == "__main__":
    # Begin client.
    client = Client()

    # Infinite loop while quadrotor is running.
    # Note: It is difficult to end python threads gracefully, ESPECIALLY when the threads on blocking on I/O. 
    # Unfortunately, we have to Ctrl-Z when server is not running, but Ctrl-C will work when server is up, thanks to terminate calls. This is because only the main thread receives Ctrl-C
    main_loop(client)


        
