#!/usr/bin/env python

class Config:
    # Serial configuration
    baudrate = 115200
    tty = '/dev/ttyUSB1'
    # Port numbers are set arbitrarily high so as not to conflict with established port numbers
    host = ''
    recv_port = 51425
    bcast_port = 51423
    max_queue_len = 20
