from pyRF24 import pyRF24
pipes = [0xF0F0F0F0E1, 0xF0F0F0F0E2]
radio = pyRF24("/dev/spidev0.0", 8000000, 18, retries = (15, 15), channel = 76, dynamicPayloads = True, autoAck = True)
radio.openWritingPipe(pipes[0])
radio.openReadingPipe(1, pipes[1])

def recv():
#	radio.openWritingPipe(pipes[1])
#	radio.openReadingPipe(1, pipes[1])
	radio.startListening()
#	print("Recv mode")

def send():
#	radio.openWritingPipe(pipes[0])
#	radio.openReadingPipe(1, pipes[1])
	radio.stopListening()
#	print("Send mode")

