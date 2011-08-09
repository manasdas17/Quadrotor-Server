#!/usr/bin/env python

import time
import threading
from client import Quadrotor, main_loop

class Client:
    def __init__(self):
        # Set up quadrotor
        self.qrotor = Quadrotor()
        # self.qrotor.register_callback(self.callback)

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
#        while (not self.stop.wait(1)):
        while (not self.stop.is_set()):
            x = self.qrotor.pop()
            print "Received:",x
            time.sleep(1)
            self.qrotor.send(x)
            time.sleep(1)
            counter += 1

    def terminate(self):
        print "Terminating client."
        self.stop.set()
        self.thread.join()
        print "Client terminated."


if __name__ == "__main__":
    print "     _/_/        _/_/_/  _/        _/_/_/  _/_/_/_/  _/      _/  _/_/_/_/_/   "
    print "  _/    _/    _/        _/          _/    _/        _/_/    _/      _/        "
    print " _/  _/_/    _/        _/          _/    _/_/_/    _/  _/  _/      _/         "
    print "_/    _/    _/        _/          _/    _/        _/    _/_/      _/          "
    print " _/_/  _/    _/_/_/  _/_/_/_/  _/_/_/  _/_/_/_/  _/      _/      _/          "
    print
    print "Jeremy Nash"
    print "nashj@umich.edu"
    print
    client = Client()
    main_loop(client)
