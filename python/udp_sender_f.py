#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import struct
import math
import numpy
from gnuradio import gr

class udp_sender_f(gr.sync_block):
    """
    docstring for block udp_sender_f
    """
    def __init__(self):
        gr.sync_block.__init__(self, name="udp_sender_f", in_sig=[numpy.float32], out_sig=None)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udpAddress = ('localhost', 10000)

    def work(self, input_items, output_items):
        for pulseValue in input_items[0]:
            if math.isnan(pulseValue):
                continue
            if pulseValue > 0:
                self.sock.sendto(struct.pack('<f', pulseValue), self.udpAddress)
        return len(input_items[0])

