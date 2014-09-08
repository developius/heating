from pyRF24 import pyRF24
import time, mode
radio = pyRF24("/dev/spidev0.0", 8000000, 18, retries = (15, 15), channel = 76, dynamicPayloads = True, autoAck = True)

while True:
#	mode.send()
	inputed = input("Node: ")
	while not radio.write(str(inputed + "temp")):
		print("Failed")
	print("Sent")
	mode.recv()
	time.sleep(0.25)
	if radio.available():
		payload = radio.read(radio.getDynamicPayloadSize())
		if payload is not None: print("Got: %s" % payload)
	
"""for i in range(0,101):
	if radio.write(str(i)): print(i, "sent")
	time.sleep(0.25)"""
