#!/usr/bin/python3
from pyRF24 import pyRF24
import time, binascii, time, os, sys, gspread, datetime, json, mysql.connector
from urllib import request

credentials = []

for line in open("credentials.txt", "r"):
	credentials.append(line.split("\n")[0])
connection = {"sql":False,"gs":False}

# 8000000
radio = pyRF24("/dev/spidev0.0", 9600, 25, retries = (15, 15), channel = 76, dynamicPayloads = True, autoAck = True)
radio.setDataRate(2)
pipes = [0xF0F0F0F0E1, 0xF0F0F0F0E2]
radio.openWritingPipe(pipes[0])
radio.openReadingPipe(1, pipes[1])

last_threshold = {}
last_status = {}
node_temp = {}
nodes = [0]

for node in nodes:
	node_temp["%i" % node] = None
	last_threshold["%i" % node] = []
	for i in range(0,24):
		last_threshold["%i" % node].append(None)
	node_temp["%i" % node] = None
	last_status["%i" % node] = None

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

while True:
	try:
		db = mysql.connector.connect(user=credentials[1], password=credentials[2], host=credentials[0], database=credentials[3], autocommit = True)
		cur = db.cursor()
		connection['sql'] = True
	except:
		connection['sql'] = False
	try:
		gc = gspread.login(credentials[4], credentials[5])
		ws = gc.open("Heating Data").sheet1
		connection['gs'] = True
	except:
		connection['gs'] = False

	if connection['sql']:
		for node in nodes:
			changed = False
			send()
			timeout = False
			started_waiting_at = time.time()
			while not radio.write(str(str(node) + "temp")) and not timeout:
				if ((time.time() - started_waiting_at) > 5): timeout = True
			if timeout: print("Node %i down" % node); break
	#			cur.execute("UPDATE node_data SET Status='%s' WHERE Node='%i';" % ("off", node))
	#			cur.execute("UPDATE node_data SET Status='%s' WHERE Node='%i';" % ("on", node)) # is supposed to detect if node is up but if
															# you turn off the node in the db, it turns
															# it back off
			hour = datetime.datetime.now().hour
			print("Hour: %i" % hour)
			recv()
			timeout = False
			started_waiting_at = time.time()
			while not radio.available() and not timeout:
				if ((time.time() - started_waiting_at) > 5): timeout = True
			if timeout: break
			else:
				try:
					payload = radio.read(radio.getDynamicPayloadSize())
					temp = binascii.hexlify(payload)
					temp = temp.decode('ascii')
					temp = int(str(int(temp, 16)))
					cur.execute("UPDATE temp_log SET %s='%.1f' WHERE Hour='%i';" % ("Node" + str(node), float(temp), hour))
					cur.execute("UPDATE node_data SET Temperature='%.1f' WHERE Node='%i';" % (float(temp), node))
					node_temp["%i" % node] = temp
					print("Node %i %.2f" % (node, temp))
				except ValueError:
					print("Failed to get temp from node: %i" % node)

			cur.execute("SELECT %s from node_threshold WHERE `Hour`='%i'" % ("Node" + str(node), hour))
			for Threshold in cur:
				Threshold = int(Threshold[0])
				if Threshold != last_threshold["%i" % node][hour]:
					print("	| Change with thresholds: %s" % Threshold)
					last_threshold["%i" % node][hour] = Threshold
					changed = True

			cur.execute("SELECT Status from node_data WHERE `Node`='%i'" % node)
			for Status in cur:
				Status = Status[0]
				if Status == "on": Status = 1
				if Status == "off": Status = 0
				if Status != last_status["%i" % node]:
					print("	| Change with device status: %s" % Status)
					last_status['%i' % node] = Status
					changed = True
			if changed == True:
				send()
				timeout = False
				print("	| Sending " + str(node) + str(last_threshold["%i" % node][hour]) + str(last_status["%i" % node]) + "...", end="")
				started_waiting_at = time.time()
				while not radio.write(str(node) + str(last_threshold["%i" % node][hour]) + str(last_status["%i" % node])) and not timeout:
					if ((time.time() - started_waiting_at) > 5): timeout = True
				if timeout:
					print("	failed")
					last_threshold["%i" % node][hour] = None # --| next time round it's still different so that we retry to update the node
					last_status["%i" % node] = None		 # --| ''
				else:
					print(" sent")
			time.sleep(10)
		if connection['gs']:
			try:
				ws.append_row([time.strftime("%Y-%m-%d %H:%M:%S"), node_temp["0"], node_temp["1"], node_temp["2"], ext_temp()])
			except:
				pass
		cur.close()
		db.close()
