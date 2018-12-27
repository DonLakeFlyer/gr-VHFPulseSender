#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import struct
import math
import numpy
import CommandParser
import time
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

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 0)
        self.socket.setblocking(False)
        self.udpAddress = (MCAST_GRP, MCAST_PORT)

        self.pulseDetectBase = None
        self.lastPulseTime = time.time()

    def work(self, input_items, output_items):
        for pulseValue in input_items[0]:
            try:
                data = self.socket.recv(1024)
            except:
                pass
            else:
                self.parseCommand(data)
            if math.isnan(pulseValue):
                continue
            if pulseValue > 0:
                temp = 0
                if self.cpuTemp:
                    temp = self.cpuTemp.temperature
                self.socket.sendto(struct.pack('<iff', self.channelIndex, pulseValue, temp), self.udpAddress)
                self.lastPulseTime = time.time()
            elif time.time() - self.lastPulseTime > 3:
                temp = 0
                if self.cpuTemp:
                    temp = self.cpuTemp.temperature
                self.socket.sendto(struct.pack('<iff', self.channelIndex, 0, temp), self.udpAddress)
                self.lastPulseTime = time.time()

        return len(input_items[0])


    def setPulseDetectBase(self, pulseDetectBase):
        self.pulseDetectBase = pulseDetectBase

    def parseCommand(self, commandBytes):
        command, value = struct.unpack_from('<ii', commandBytes)
        if command == 1:
            print("Gain changed ", value)
            self.pulseDetectBase.set_gain(value)
        elif command == 2: 
            print("Frequency changed ", value)
            self.pulseDetectBase.set_pulse_freq(value)
        else:
            print("Unknown command ", command, len(commandBytes))
