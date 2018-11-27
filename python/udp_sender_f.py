#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import struct
import math
import numpy
import CommandParser
from gnuradio import gr

class udp_sender_f(gr.sync_block):
    """
    docstring for block udp_sender_f
    """
    def __init__(self):
        gr.sync_block.__init__(self, name="udp_sender_f", in_sig=[numpy.float32], out_sig=None)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setblocking(False)
        self.udpAddress = ('localhost', 10000)

        self.pulseDetectBase = None

    def work(self, input_items, output_items):
        for pulseValue in input_items[0]:
            try:
                data = self.sock.recv(1024)
            except:
                pass
            else:
                parseCommand(data, self.pulseDetectBase)
            if math.isnan(pulseValue):
                continue
            if pulseValue > 0:
                self.sock.sendto(struct.pack('<f', pulseValue), self.udpAddress)
        return len(input_items[0])


    def setPulseDetectBase(self, pulseDetectBase):
        self.pulseDetectBase = pulseDetectBase
