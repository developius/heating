#!/usr/bin/python
from pyRF24 import pyRF24
import time, binascii, time, os, sys, gspread, datetime, json, mysql.connector
from urllib import request
import urllib

credentials = []

for line in open("credentials.txt", "r"):
	credentials.append(line.split("\n")[0])

connection = {"sql":False,"gs":False}

print("Connecting to MySQL database... ", end="")
try:
	db = mysql.connector.connect(user=credentials[1], password=credentials[2], host=credentials[0], database=credentials[3], autocommit = True)
	cur = db.cursor()
	connection['sql'] = True
	print("Connected")
except:
	connection['sql'] = False
	print("Failed")

print("Connecting to GS... ", end="")
try:
	gc = gspread.login(credentials[4], credentials[5])
	ws = gc.open("Heating Data").sheet1
	connection['gs'] = True
	print("Connected")
except:
	connection['gs'] = False
	print("Failed")


def ext_temp():
	req = request.urlopen('http://api.openweathermap.org/data/2.5/find?q=laxfield&units=metric')
	encoding = req.headers.get_content_charset()
	obj = json.loads(req.read().decode(encoding))
	return round(obj['list'][0]['main']['temp'], 1)

while True:
	if connection['sql']:
		hour = datetime.datetime.now().hour
		try:
			temp = ext_temp()
			print("Temp: %s" % temp)
		except:
			print("Failed to get temp")
			temp = None
		if temp:
			cur.execute("UPDATE ext_temp_log SET `Temp`='%.1f' WHERE `Hour`='%i'" % (temp, hour))
	time.sleep(60)
