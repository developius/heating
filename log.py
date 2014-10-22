#!/usr/bin/python3
from pyRF24 import pyRF24
import time, binascii, time, os, sys, gspread, datetime, json, mysql.connector
from urllib import request

credentials = []

for line in open("credentials.txt", "r"):
	credentials.append(line.split("\n")[0])
connection = {"sql":False,"gs":False}

def ext_temp():
	req = request.urlopen('http://api.openweathermap.org/data/2.5/find?q=laxfield&units=metric')
	encoding = req.headers.get_content_charset()
	obj = json.loads(req.read().decode(encoding))
	return obj['list'][0]['main']['temp']

nodes=[0]
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
			cur.execute("SELECT `Temperature` FROM `node_data` WHERE `Node`=%i" % node);
			for Temperature in cur:
				temp = Temperature[0]
			print(temp,ext_temp())
			cur.execute("INSERT INTO `log` (`Ext_Temp`,`Node0`) VALUES (%.2f, %.2f);" % (temp,ext_temp()))
		cur.close()
		db.close()
	time.sleep(30*60)
