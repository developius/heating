from pyRF24 import pyRF24
import time, binascii
import mode # sets up pipes
radio = pyRF24("/dev/spidev0.0", 8000000, 18, retries = (15, 15), channel = 76, dynamicPayloads = True, autoAck = True)

while True:
#	mode.send() calls radio.stopListening()
	inputed = input("Node: ")
	while not radio.write(str(inputed + "temp")):
		print("Failed")
	print("Sent")
	mode.recv() # calls radio.startListening()
	time.sleep(0.25)
	if radio.available():
		payload = radio.read(radio.getDynamicPayloadSize())
		if payload:
			payload = binascii.hexlify(payload)
			payload = payload.decode('ascii')
			payload = str(int(payload, 16))
			print("Got: %s" % payload)
