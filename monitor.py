#!/usr/bin/python3
from pyRF24 import pyRF24
import time, binascii, time, os, sys, gspread, datetime, json, mysql.connector
from urllib import request

credentials = []

for line in open("credentials.txt", "r"):
	credentials.append(line.split("\n")[0])

db = mysql.connector.connect(user=credentials[1], password=credentials[2], host=credentials[0], database=credentials[3], autocommit = True)
cur = db.cursor()

"""try:
	gc = gspread.login(credentials[4], credentials[5])
	ws = gc.open("Heating Data").sheet1
except:
	print("Unable to connect to Google Spreadsheet")"""

radio = pyRF24("/dev/spidev0.0", 8000000, 18, retries = (15, 15), channel = 76, dynamicPayloads = True, autoAck = True)
radio.setDataRate(2)
pipes = [0xF0F0F0F0E1, 0xF0F0F0F0E2]
radio.openWritingPipe(pipes[0])
radio.openReadingPipe(1, pipes[1])

last_threshold = {"0": [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None]}
last_status = {"0": ""}
last_night_status = {"0": ""}
last_day_status = {"0": ""}
node_temp = {"0": None, "1": None, "2": None}
nodes = [0]
update_payload = [None,None]

def ext_temp():
        req = request.urlopen('http://api.openweathermap.org/data/2.5/find?q=laxfield&units=metric')
        encoding = req.headers.get_content_charset()
        obj = json.loads(req.read().decode(encoding))
        return obj['list'][0]['main']['temp']

def recv():
	radio.startListening()
	time.sleep(0.25)

def send():
	radio.stopListening()
	time.sleep(0.25)

def day(): # work out if day or night
	now = datetime.datetime.now()
	if now.hour >= 10 and now.hour <= 7: return False
	else: return True

while True:
	for node in nodes:
		changed = False
		send()
		timeout = False
		started_waiting_at = time.time()
		while not radio.write(str(str(node) + "temp")) and not timeout:
			if ((time.time() - started_waiting_at) > 5): timeout = True
		if timeout: break
#			cur.execute("UPDATE heating.node_data SET Status='%s' WHERE Node='%i';" % ("off", node))
#			cur.execute("UPDATE heating.node_data SET Status='%s' WHERE Node='%i';" % ("on", node)) # is supposed to detect if node is up but if
														# you turn off the node in the db, it turns
														# it back off
		hour = datetime.datetime.now().hour
		recv()
		timeout = False
		started_waiting_at = time.time()
		while not radio.available() and not timeout:
			if ((time.time() - started_waiting_at) > 5): timeout = True
		if timeout: break
		else:
			payload = radio.read(radio.getDynamicPayloadSize())
			temp = binascii.hexlify(payload)
			temp = temp.decode('ascii')
			temp = int(str(int(temp, 16)))
			cur.execute("UPDATE heating.temp_log SET %s='%.1f' WHERE Hour='%i';" % ("Node" + str(node), float(temp), hour))
			cur.execute("UPDATE heating.node_data SET Temperature='%.1f' WHERE Node='%i';" % (float(temp), node))
			node_temp["%i" % node] = temp
			print("Node %i %.2f" % (node, temp))

		cur.execute("SELECT * from heating.node_threshold WHERE %i='%i'" % (hour, hour))
		for Threshold in cur:
			if Threshold[hour + 1] != last_threshold["%i" % node][hour]: # [hour + 1] allows for 0th index
				print("		Change with thresholds: %i" % Threshold[hour + 1])
				last_threshold["%i" % node][hour] = int(Threshold[hour + 1])
				changed = True

		cur.execute("SELECT Status from heating.node_data WHERE Node='%i'" % node)
		for Status in cur:
			if Status[0] == "on": Status = "1"
			if Status[0] == "off": Status = "0"
			if Status != last_status["%i" % node]:
				print("		Change with device status")
				last_status['%i' % node] = Status
				changed = True
		time.sleep(1)
		if changed == True:
			send()
			time.sleep(0.25)
			timeout = False
			print("		Sending " + str(node) + str(last_threshold["%i" % node][hour]) + str(last_status["%i" % node]))
			started_waiting_at = time.time()
			while not radio.write(str(node) + str(last_threshold["%i" % node][hour]) + str(last_status["%i" % node])) and not timeout: # never works
				if ((time.time() - started_waiting_at) > 5): timeout = True
			if timeout:
				print("		Could not update node %i" % node)
				last_threshold["%i" % node][hour] = None # --| next time round it's still different so that we retry to update the node
				last_status["%i" % node] = None		 # --| ''
				break
		time.sleep(1)
#	try:
#		ws.append_row([time.strftime("%Y-%m-%d %H:%M:%S"), node_temp["0"], node_temp["1"], node_temp["2"], ext_temp()])
#	except:
#		print("Insert into GS failed")
