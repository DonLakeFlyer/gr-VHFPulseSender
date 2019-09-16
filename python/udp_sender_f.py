#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import select
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
        self.sendIndex = 0

        if gpiozerioAvailable:
            self.cpuTemp = CPUTemperature()
        else:
            self.cpuTemp = None

        self.udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        if localhost == 1:
            # VHF Drone
            self.udpSocket.bind(('localhost', 10001))
            self.sendAddress = ('localhost', 10000) 
        else:
            # STE Tracker

            self.udpSocket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 0)
            self.sendAddress = ('224.0.0.1', 5007) 

            self.tcpSocketServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcpSocketServer.setblocking(0)
            self.tcpAddress = ('127.0.0.1', 5005)
            self.tcpSocketServer.bind(self.tcpAddress)
            self.tcpSocketServer.listen(1)
            self.tcpClient = None

        self.udpSocket.setblocking(False)

        self.pulseDetectBase = None
        self.lastPulseTime = time.time()

        self.printOnce = True
        self.localhost = localhost

    def work(self, input_items, output_items):
        if self.printOnce:
            print (self.sendAddress, self.localhost)
            self.printOnce = False

        for pulseValue in input_items[0]:
            # First see if we have a tcp connection
            inputs = [ self.tcpSocketServer ]
            outputs = []
            readable, writable, exceptional = select.select(inputs, outputs, inputs, 0)
            for s in readable:
                if s is server:
                    print("TCP client accepting", client_address)
                    self.tcpClient, client_address = s.accept()

            # Check for incoming commands
            if self.tcpClient:
                try:
                    data = self.tcpClient.recv(1024)
                except:
                    pass
                else:
                    self.parseCommand(data)

            if math.isnan(pulseValue):
                continue

            temp = 0
            if self.cpuTemp:
                temp = self.cpuTemp.temperature

            sendPulse = False
            if pulseValue > 0:
                sendPulse = True
            elif time.time() - self.lastPulseTime > 3:
                sendPulse = True

            if sendPulse:
                packedData = struct.pack('<iiffii', 
                                self.sendIndex,
                                self.channelIndex, 
                                pulseValue, 
                                temp, 
                                self.pulseDetectBase.get_pulse_freq(),
                                self.pulseDetectBase.get_gain())
                try:
                    self.udpSocket.sendto(packedData, self.sendAddress)
                except Exception as e:
                    print("Exception udp_sender:work Sending pulse to UDP socket", e)
                if self.tcpClient:
                    try:
                        self.tcpClient.sendall(packedData)
                    except Exception as e:
                        print("Exception udp_sender:work Sending pulse to TCP socket", e)
                self.lastPulseTime = time.time()
                self.sendIndex = self.sendIndex + 1

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
