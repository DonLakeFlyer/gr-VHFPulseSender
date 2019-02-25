#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import struct
import math
import numpy
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
    def __init__(self, channel_index, localhost):
        gr.sync_block.__init__(self, name="udp_sender_f", in_sig=[numpy.float32], out_sig=None)

        self.channelIndex = channel_index

        if gpiozerioAvailable:
            self.cpuTemp = CPUTemperature()
        else:
            self.cpuTemp = None

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if localhost == 1:
            # VHF Drone
            self.socket.bind(('localhost', 10001))
            self.sendAddress = ('localhost', 10000) 
        else:
            # STE Tracker
            self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 0)
            self.sendAddress = ('224.0.0.1', 5007) 
        self.socket.setblocking(False)

        self.pulseDetectBase = None
        self.lastPulseTime = time.time()

        self.printOnce = True
        self.localhost = localhost

    def work(self, input_items, output_items):
        if self.printOnce:
            print (self.sendAddress, self.localhost)
            self.printOnce = False
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
                try:
                    self.socket.sendto(struct.pack('<iffi', self.channelIndex, pulseValue, temp, self.pulseDetectBase.get_gain()), self.sendAddress)
                except Exception as e:
                    print("Exception udp_sender:work valid pulse send", e)
                self.lastPulseTime = time.time()
            elif time.time() - self.lastPulseTime > 3:
                temp = 0
                if self.cpuTemp:
                    temp = self.cpuTemp.temperature
                try:
                    self.socket.sendto(struct.pack('<iffi', self.channelIndex, 0, temp, self.pulseDetectBase.get_gain()), self.sendAddress)
                except Exception as e:
                    print("Exception udp_sender:work no pulse send", e)
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
