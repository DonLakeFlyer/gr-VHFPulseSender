#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy
import math
from gnuradio import gr
from bluetooth import *

class bt_sender_f(gr.sync_block):
    """
    docstring for block bt_sender_f
    """
    def __init__(self, channel_index):
        gr.sync_block.__init__(self, name="bt_sender_f", in_sig=[numpy.float32], out_sig=None)

        self.channelIndex = channel_index

        self.pulseDetectBase = None

        self.clientSocket = None
        self.serverSocket = BluetoothSocket (RFCOMM)
        self.serverSocket.bind(("", PORT_ANY))
        self.serverSocket.listen(1)

        uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
        advertise_service(self.serverSocket,
                            "PulseServer " + str(channel_index),
                            service_id = uuid,
                            service_classes = [ uuid, SERIAL_PORT_CLASS ],
                            profiles = [ SERIAL_PORT_PROFILE ])
        self.serverSocket.setblocking(False)

    def work(self, input_items, output_items):
        if not self.clientSocket:
            try:
                self.clientSocket, clientInfo = self.serverSocket.accept()
            except:
                pass
            else:
                print("Accepted connection from ", clientInfo)
        if self.pulseDetectBase:
            self.pulseDetectBase.set_vga_gain(15)
        for pulseValue in input_items[0]:
            if math.isnan(pulseValue):
                continue
            if pulseValue > 0 and self.clientSocket:
                self.clientSocket.send(str(self.channelIndex) + " " + str(pulseValue) + "\n")
        return len(input_items[0])

    def setPulseDetectBase(self, pulseDetectBase):
        self.pulseDetectBase = pulseDetectBase
