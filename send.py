from pyRF24 import pyRF24
import time, binascii
radio = pyRF24("/dev/spidev0.0", 8000000, 18, retries = (15, 15), channel = 76, dynamicPayloads = True, autoAck = True)

def recv():
	radio.startListening()

def send(): 
	radio.stopListening()


while True:
	message = input("Message: ")
	if message == "exit": break
	send()
	while not radio.write(str(message)):
		print(message, "failed")
	print("Sent", message)
	recv()
	time.sleep(0.25)
	if radio.available():
		payload = radio.read(radio.getDynamicPayloadSize())
		if payload:
			payload = binascii.hexlify(payload)
			payload = payload.decode('ascii')
			payload = str(int(payload, 16))
			print("Got: %s" % payload)
