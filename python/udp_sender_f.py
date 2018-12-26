#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import struct
import math
import numpy
import CommandParser
from gnuradio import gr

try:
    from gpiozero import CPUTemperature
except:
    gpiozerioAvailable = False
else:
    gpiozerioAvailable = True

class udp_sender_f(gr.sync_block):
    """
    docstring for block udp_sender_f
    """
    def __init__(self, channel_index):
        gr.sync_block.__init__(self, name="udp_sender_f", in_sig=[numpy.float32], out_sig=None)

        self.channelIndex = channel_index

        if gpiozerioAvailable:
            self.cpuTemp = CPUTemperature()
        else:
            self.cpuTemp = None

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setblocking(False)
        self.udpAddress = ('224.0.0.1', 5007)

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
                temp = 0
                if self.cpuTemp:
                    temp = self.cpuTemp.temperature
                self.sock.sendto(struct.pack('<iff', self.channelIndex, pulseValue, temp), self.udpAddress)
        return len(input_items[0])


    def setPulseDetectBase(self, pulseDetectBase):
        self.pulseDetectBase = pulseDetectBase
