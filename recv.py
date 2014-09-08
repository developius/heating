from pyRF24 import pyRF24
import time, mode
radio = pyRF24("/dev/spidev0.0", 8000000, 18, retries = (15, 15), channel = 76, dynamicPayloads = True, autoAck = True)

mode.recv()
payload = None
radio.startListening()
while True:
	if radio.available():
		radio.read(payload)
		if payload: print(payload)
