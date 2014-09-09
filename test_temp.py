from pyRF24 import pyRF24
import time, binascii
radio = pyRF24("/dev/spidev0.0", 8000000, 18, retries = (15, 15), channel = 76, dynamicPayloads = True, autoAck = True)
pipes = [0xF0F0F0F0E1, 0xF0F0F0F0E2]
radio.openWritingPipe(pipes[0]) 	
radio.openReadingPipe(1, pipes[1])

def recv():
	radio.startListening()

def send(): 
	radio.stopListening()

while True:
	send()
	inputed = input("Node: ")
	while not radio.write(str(inputed + "temp")):
		print("Failed")
	print("Sent")
	recv()
	time.sleep(0.25)
	if radio.available():
		payload = radio.read(radio.getDynamicPayloadSize())
		if payload:
			payload = binascii.hexlify(payload)
			payload = payload.decode('ascii')
			payload = str(int(payload, 16))
			print("Got: %s" % payload)
