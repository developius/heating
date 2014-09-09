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

sent_thresholds = {"1": 16}
nodes = [0]

def recv():
	radio.startListening()

def send():
	radio.stopListening()

while True:
	for node in nodes:
		print("Node %i" % node)
		send()
		if not radio.write(str(str(node) + "temp")):
			cur.execute("UPDATE heating.node_data SET Status='%s' WHERE Node='%i';" % ("off", node))
			print("down")
			break
		print("Sent")
		recv()
		time.sleep(0.25)
		if radio.available():
			payload = radio.read(radio.getDynamicPayloadSize())
			if payload:
				temp = binascii.hexlify(payload)
				temp = temp.decode('ascii')
				temp = int(str(int(temp, 16)))
				print("Temp %i" % temp)
				cur.execute("UPDATE heating.node_data SET Temperature='%.1f', Status='%s' WHERE Node='%i';" % (float(temp), "on", node))
				ws.append_row([time.strftime("%d/%m/%Y %H:%M:%S"),float(temp)])
			else:
				cur.execute("UPDATE heating.node_data SET Status='%s' WHERE Node='%i';" % ("off", node))
		else:
			cur.execute("UPDATE heating.node_data SET Status='%s' WHERE Node='%i';" % ("off", node))

		time.sleep(1)

"""		if mysql_db_threshold[node] != sent_threshold[node]:
			print("Found threshold change with node %i" % node)
			out = "1" + threshold
			radio.write(out,len(out))
		if mysql_db_scheldule[node] != schedule[node]:
			print("Found schedule change with node %i" % node)
			scedule[node] = mysql_db_schedule[node]"""
