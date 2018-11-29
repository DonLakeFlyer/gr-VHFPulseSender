def parseCommand(commandStr, pulseDetectBase):
	args = commandStr.split(" ")
	if len(commandStr) == 0 or not pulseDetectBase:
		return
	# There might be multiple commands received at the same time
	last = len(args) - 1
	if last <= 0:
		return
	command = args[len -1]
	value = int(args[len])
	if command == "gain":
		print("Gain changed ", value)
		pulseDetectBase.set_vga_gain(value)
	elif command == "freq":	
		print("Frequency changed ", value)
		pulseDetectBase.set_pulse_freq(value)
	else:
		print("Unknown command ", command)
