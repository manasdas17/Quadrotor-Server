#!/usr/bin/env python

import socket
import serial
import threading
import sys
from config import Config

class NetworkThread:
    def __init__(self, ser):
        # We need to create a separate port from our broadcast port, otherwise we receive all of the broadcast messages!
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.bind((Config.host, Config.recv_port))

        # Serial connection
        self.ser = ser

        # Set up threading
        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True
        self.stop = threading.Event()
        self.thread.start()

    def run(self):
        while 1:
            try: 
                # Can we add a timeout here?
                message, address = self.sock.recvfrom(8192)
                print "Received data from", address, ":", message
                self.ser.write(message)
            except (KeyboardInterrupt, SystemExit):
                raise
    
    def terminate(self):
        print "Terminating network thread."
        self.stop.set()
        self.thread.join()
        print "Network thread terminated." 


class SerialThread:
    def __init__(self, ser):
        # Set up socket network connection
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.bind((Config.host, Config.bcast_port))
        
        # Serial
        self.ser = ser

        # Set up threading
        self.thread = threading.Thread(target=self.run)
        self.stop = threading.Event()
        self.thread.daemon = True
        self.thread.start()

    def run(self):
        while (not self.stop.is_set()):
            try:
                line = self.ser.readline()
                # line = "x 234 y 321 z 330 "
                self.sock.sendto(line, ('<broadcast>', Config.bcast_port))
                # print "Broadcasting:", line
            except (KeyboardInterrupt, SystemExit):
                raise

    def terminate(self):
        print "Terminating serial thread."
        self.stop.set()
        self.thread.join()
        print "Serial thread terminated."

if __name__ == "__main__":
    print
    print "     _/_/        _/_/_/  _/_/_/_/  _/_/_/    _/      _/   "
    print "  _/    _/    _/        _/        _/    _/  _/      _/    "
    print " _/  _/_/      _/_/    _/_/_/    _/_/_/    _/      _/     "
    print "_/    _/          _/  _/        _/    _/    _/  _/        "
    print " _/_/  _/  _/_/_/    _/_/_/_/  _/    _/      _/           "
    print
    print "Jeremy Nash"
    print "nashj@umich.edu"
    print 
    # Set up serial connection
    try:
        ser = serial.Serial(Config.tty, Config.baudrate)
    except serial.SerialException:
        print "Error: can not find", Config.tty
        print "You probably forgot to plug in the Arduino... again."
        sys.exit(0)

    # Set up threads
    ser_thread = SerialThread(ser)
    net_thread = NetworkThread(ser)
    
    # Infinite loop
    while 1:
        try:
            dummy = None
        except (KeyboardInterrupt, SystemExit):
            print "Main thread keyboard interrupt"
            PLEASESTOP
            ser_thread.terminate()
            net_thread.terminate()
            sys.exit()

