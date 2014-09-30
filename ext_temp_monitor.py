#!/usr/bin/python
from pyRF24 import pyRF24
import time, binascii, time, os, sys, gspread, datetime, json, mysql.connector
from urllib import request

credentials = []

for line in open("credentials.txt", "r"):
	credentials.append(line.split("\n")[0])

db = mysql.connector.connect(user=credentials[1], password=credentials[2], host=credentials[0], database=credentials[3], autocommit = True)
cur = db.cursor()

#gc = gspread.login(credentials[4], credentials[5])
#ws = gc.open("Heating Data").sheet1

def ext_temp():
	req = request.urlopen('http://api.openweathermap.org/data/2.5/find?q=laxfield&units=metric')
	encoding = req.headers.get_content_charset()
	obj = json.loads(req.read().decode(encoding))
	return round(obj['list'][0]['main']['temp'], 1)

while True:
	hour = datetime.datetime.now().hour
	try:
		cur.execute("UPDATE heating.ext_temp_log SET `0%i`='%i'" % (hour, ext_temp()))
		print(ext_temp())
	except urllib.error.HTTPError as error:
		print("Failed to get temp: %s" % error)
	time.sleep(5) # * 60
