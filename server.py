#!/usr/bin/env python

import socket
import serial
import threading
import sys
from config import Config

def network_thread(ser):
    # We need to create a separate port from our broadcast port, otherwise we receive all of the broadcast messages!
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind((Config.host, Config.recv_port))

    while 1:
        try: 
            message, address = sock.recvfrom(8192)
            print "Got data from", address, ":", message
            ser.write(message)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            traceback.print_exc()



def serial_thread(ser):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind((Config.host, Config.bcast_port))

    while 1:
        try:
            line = ser.readline()
            sock.sendto(line, ('<broadcast>', Config.bcast_port))
            print "Broadcasting:", line
        except (KeyboardInterrupt, SystemExit):
            raise


if __name__ == "__main__":
    # Set up serial connection
    try:
        ser = serial.Serial(Config.tty, Config.baudrate)
    except serial.SerialException:
        print "Error: can not find", Config.tty
        print "You probably forgot to plug in the Arduino... again."
        sys.exit(0)

    # Set up threads
    threading.Thread(target=serial_thread, args=(ser,)).start()
    threading.Thread(target=network_thread, args=(ser,)).start()
    
    # Infinite loop
    while 1:
        try:
            dummy = None
        except (KeyboardInterrupt, SystemExit):
            print "Main thread keyboard interrupt"
            msg_queue.terminate()
            client.terminate()
            sys.exit()

