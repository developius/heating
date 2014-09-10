#!/usr/bin/python
from pyRF24 import pyRF24
import time, binascii, time, os, sys, gspread, datetime, json, mysql.connector
from urllib import request

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
last_night_status = {"0": ""}
last_day_status = {"0": ""}
nodes = [0]

def recv():
	radio.startListening()

def send():
	radio.stopListening()

def day(): # work out if day or night
	now = datetime.datetime.now()
	if now.hour >= 10 and now.hour <= 7: return False
	else: return True

def ext_temp():
	req = request.urlopen('http://api.openweathermap.org/data/2.5/find?q=laxfield&units=metric')
	encoding = req.headers.get_content_charset()
	obj = json.loads(req.read().decode(encoding))
	return obj['list'][0]['main']['temp']

while True:
	print(ext_temp())
	for node in nodes:
		send()
		if not radio.write(str(str(node) + "temp")):
			cur.execute("UPDATE heating.node_data SET Status='%s' WHERE Node='%i';" % ("off", node))
			print("Down")
			break
#		cur.execute("UPDATE heating.node_data SET Status='%s' WHERE Node='%i';" % ("on", node)) # is supposed to detect if node is up but if
													# you turn off the node in the db, this turns
													# it back on
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

		cur.execute("SELECT Threshold, Status, Night_Status, Day_Status FROM heating.node_data WHERE Node='%i'" % node)
		for Threshold, Day_Status, Night_Status, Status in cur:
			if Threshold != last_threshold["%i" % node]:
#				print("Thresholds are not the same for node %i" % node)
				last_threshold["%i" % node] = Threshold
			if Status == "on": Status = "1"
			if Status == "off": Status = "0"
			if Status != last_status["%i" % node]:
#				print("The status is not the same for node %i" % node)
				last_status["%i" % node] = Status
			send()
			if (Day_Status != last_day_status["%i" % node]):
#				print("Day_Status is not the same for node %i" % node)
				last_day_status["%i" % node] = Day_Status

			if (Night_Status != last_night_status["%i" % node]):
#                                print("Night_Status is not the same for node %i" % node)
                                last_night_status["%i" % node] = Night_Status

			if (last_day_status["%i" % node] == "off" and day()) or (last_night_status["%i" % node] == "on" and not day()): # we want it off because of the time
				last_status["%i" % node] = "0"

			while not radio.write(str(node) + str(last_threshold["%i" % node]) + str(last_status["%i" % node])):
				pass
			print("Sent: " + str(node) + str(last_threshold["%i" % node]) + str(last_status["%i" % node]))
			recv()
		time.sleep(10)
