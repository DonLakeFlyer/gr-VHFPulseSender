#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy
from gnuradio import gr
from bluetooth import *

class bt_sender_f(gr.sync_block):
    """
    docstring for block bt_sender_f
    """
    def __init__(self):
        gr.sync_block.__init__(self, name="bt_sender_f", in_sig=[numpy.float32], out_sig=None)

        self.clientSocket = None
        self.serverSocket = BluetoothSocket (RFCOMM)
        self.serverSocket.bind(("", PORT_ANY))
        self.serverSocket.listen(1)
        self.serverSocket.setblocking(False)

        uuid = "612490e5-c027-488e-b173-df985ccf2bdc"
        advertise_service(self.serverSocket,
                            "PulseServer",
                            service_id = uuid,
                            service_classes = [ uuid, SERIAL_PORT_CLASS ],
                            profiles = [ SERIAL_PORT_PROFILE ])

    def work(self, input_items, output_items):
        if not self.clientSocket:
            try:
                self.clientSocket, clientInfo = self.serverSocket.accept()
            except:
                pass
            else:
                print("Accepted connection from ", clientInfo)
                self.clientSocket.setblocking(False)
        for pulseValue in input_items[0]:
            if math.isnan(pulseValue):
                continue
            if pulseValue > 0:
                self.clientSocket.send(str(pulseValue))
        return len(output_items[0])

