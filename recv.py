from pyRF24 import pyRF24
import time
radio = pyRF24("/dev/spidev0.0", 8000000, 18, retries = (15, 15), channel = 76, dynamicPayloads = True, autoAck = True)

def recv():
	radio.startListening()

def send():
	radio.stopListening()

recv()
while True:
	if radio.available():
		radio.read(payload)
		if payload: print(payload)
