import threading
import math
import subprocess
import socket
import select
import struct

try:
    from gpiozero import CPUTemperature
except:
    gpiozerioAvailable = False
else:
    gpiozerioAvailable = True

class TCPThread (threading.Thread):
	exitFlag = False

	def __init__(self, pulseQueue, channelIndex, pulseDetectBase):
		threading.Thread.__init__(self)

		self.pulseQueue = pulseQueue
		self.channelIndex = channelIndex
		self.pulseDetectBase = pulseDetectBase
		self.sendIndex = 0

		if gpiozerioAvailable:
			self.cpuTemp = CPUTemperature()
		else:
			self.cpuTemp = None

		self.tcpSocketServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.tcpAddress = ('', 50000)
		self.tcpSocketServer.bind(self.tcpAddress)
		self.tcpSocketServer.listen(1)
		self.tcpClient = None

	def run(self):
		print("Waiting on TCP client connection")
		self.tcpClient, clientAddress = self.tcpSocketServer.accept()
		print("TCP connected", clientAddress)
		while True:
			pulseValue = self.pulseQueue.get(True)
			print("TCPThread pulseValue", pulseValue)

			temp = 0
			if self.cpuTemp:
				temp = self.cpuTemp.temperature

			packedData = struct.pack('<iiffii', 
							self.sendIndex,
							self.channelIndex, 
							pulseValue, 
							temp, 
							self.pulseDetectBase.get_pulse_freq(),
							self.pulseDetectBase.get_gain())
			try:
				self.tcpClient.sendall(packedData)
			except Exception as e:
				print("Exception udp_sender:work Sending pulse to UDP socket", e)
			self.sendIndex = self.sendIndex + 1

#	def foo(self):
		# First see if we have a tcp connection
		#inputs = [ self.tcpSocketServer ]
		#outputs = []
		#readable, writable, exceptional = select.select(inputs, outputs, inputs, 0)
		#for s in readable:
		#    if s is server:
		#        print("TCP client accepting", client_address)
		#        self.tcpClient, client_address = s.accept()

		# Check for incoming commands
#		if self.tcpClient:
#			try:
#				data = self.tcpClient.recv(1024)
#			except:
#				pass
#			else:
#				self.parseCommand(data)
#
#		if math.isnan(pulseValue):
#			return
#
#		temp = 0
#		if self.cpuTemp:
#			temp = self.cpuTemp.temperature
#
#		packedData = struct.pack('<iiffii', 
#						self.sendIndex,
#						self.channelIndex, 
#						pulseValue, 
#						temp, 
#						self.pulseDetectBase.get_pulse_freq(),
#						self.pulseDetectBase.get_gain())
#		try:
#			self.udpSocket.sendto(packedData, self.sendAddress)
#			self.udpSocket.sendto(packedData, self.sendAddress)
#		except Exception as e:
#			print("Exception udp_sender:work Sending pulse to UDP socket", e)
#		if self.tcpClient:
#			try:
#				self.tcpClient.sendall(packedData)
#			except Exception as e:
#				print("Exception udp_sender:work Sending pulse to TCP socket", e)
#		self.sendIndex = self.sendIndex + 1

