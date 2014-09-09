#!/usr/bin/python
from pyRF24 import pyRF24
import time, binascii, time, os, sys, gspread
import mysql.connector

credentials = []

for line in open("credentials.txt", "r"):
	credentials.append(line.split("\n")[0])

db = mysql.connector.connect(user=credentials[1], password=credentials[2], host=credentials[0], database=credentials[3], autocommit = True)
cur = db.cursor()

gc = gspread.login(credentials[4], credentials[5])
ws = gc.open("Heating Data").sheet1

radio = pyRF24("/dev/spidev0.0", 8000000, 18, retries = (15, 15), channel = 76, dynamicPayloads = True, autoAck = True)
pipes = [0xF0F0F0F0E1, 0xF0F0F0F0E2]
radio.openWritingPipe(pipes[0])
radio.openReadingPipe(1, pipes[1])

last_threshold = {"0": ""}
last_status = {"0": ""}
nodes = [0]

def recv():
	radio.startListening()

def send():
	radio.stopListening()

while True:
	for node in nodes:
		send()
		if not radio.write(str(str(node) + "temp")):
			cur.execute("UPDATE heating.node_data SET Status='%s' WHERE Node='%i';" % ("off", node))
			print("Down")
			break
		cur.execute("UPDATE heating.node_data SET Status='%s' WHERE Node='%i';" % ("on", node))
		recv()
		time.sleep(0.25)
		if radio.available():
			payload = radio.read(radio.getDynamicPayloadSize())
			if payload:
				temp = binascii.hexlify(payload)
				temp = temp.decode('ascii')
				temp = int(str(int(temp, 16)))
				cur.execute("UPDATE heating.node_data SET Temperature='%.1f' WHERE Node='%i';" % (float(temp), node))
				ws.append_row([time.strftime("%d/%m/%Y %H:%M:%S"),float(temp)])

		cur.execute("SELECT Threshold, Status FROM heating.node_data WHERE Node='%i'" % node)
		for Threshold, Status in cur:
			if Threshold != last_threshold["%i" % node]:
				print("Thresholds are not the same for node %i: %s" % (node, Threshold))
				last_threshold["%i" % node] = Threshold
			if Status == "on": Status = "1"
			if Status == "off": Status = "0"
			if Status != last_status["%i" % node]:
				print("The status is not the same for node %i: %s" % (node, Status))
				last_status["%i" % node] = Status
			send()
			while not radio.write(str(node) + str(last_threshold["%i" % node]) + str(last_status["%i" % node])):
				pass
			print("Sent: " + str(node) + str(last_threshold["%i" % node]) + str(last_status["%i" % node]))
			recv()
		time.sleep(10)
