from pyRF24 import pyRF24
import time, mode
radio = pyRF24("/dev/spidev0.0", 8000000, 18, retries = (15, 15), channel = 76, dynamicPayloads = True, autoAck = True)

mode.send()
radio.startListening()

while True:
	message = input("Message: ")
	if message == "exit": break
	radio.stopListening()
	while not radio.write(str(message)):
		print(message, "failed")
	print("Sent", message)
	radio.startListening()
#	if radio.write(str(message)): print("Sent", message)
#	else: print(message, "failed")
	time.sleep(0.25)
	
"""for i in range(0,101):
	if radio.write(str(i)): print(i, "sent")
	time.sleep(0.25)"""
