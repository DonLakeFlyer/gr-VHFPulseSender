#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import numpy
import time
from gnuradio import gr
from multiprocessing import Queue
import UDPThread

class udp_sender_f(gr.sync_block):
    """
    docstring for block udp_sender_f
    """
    def __init__(self, channel_index, localhost):
        gr.sync_block.__init__(self, name="udp_sender_f", in_sig=[numpy.float32], out_sig=None)

        self.pulseQueue = Queue()

        self.udpThread = UDPThread.UDPThread(localhost == 1, self.pulseQueue)
        self.udpThread.start()

        self.channelIndex = channel_index
        self.sendIndex = 0

        self.pulseDetectBase = None
        self.lastPulseTime = time.time()

        self.printOnce = True

    def work(self, input_items, output_items):
        for pulseValue in input_items[0]:
            sendPulse = False
            if pulseValue > 0:
                sendPulse = True
            elif time.time() - self.lastPulseTime > 3:
                sendPulse = True

            if sendPulse:
                print("Adding to queue")
                self.pulseQueue.put(pulseValue)
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
