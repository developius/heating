#!/usr/bin/python
import MySQLdb
import time, os, sys
import gdata.spreadsheet.service
from random import randint
credentials = []

for line in open("credentials.txt", r):
	credentials.append(line)

db = MySQLdb.connect(host=credentials[0], # your host, usually localhost
                     user=credentials[1], # your username
                      passwd=credentials[2], # your password
                      db=credentials[3]) # name of the data base

cur = db.cursor()
db.autocommit(True)

email = credentials[4]
password = credentials[5]
spreadsheet_key = credentials[6] # get from url with the arg key=xxx
worksheet_id = "" # 1st sheet

spr_client = gdata.spreadsheet.service.SpreadsheetsService()
spr_client.email = email
spr_client.password = password
spr_client.source = 'Heating Control'
spr_client.ProgrammaticLogin()

#cur.execute("DELETE FROM `heating`.`node_data` WHERE `node_data`.`Status` = 'on'")
def clear():
	cur.execute("delete from node_data;")
	cur.execute("SELECT * FROM node_data")
	for row in cur.fetchall():
	        print "Node: %.0f Temperature: %.1f Threshold: %.1f" % (row[0], row[1], row[2])
	sys.exit()

def val():
	return randint(1,10)

def enter_start_values():
	for i in range(12):
		temp = [20+val(),20+val(),20+val(),20+val(),20+val(),20+val(),20+val(),20+val(),20+val(),20+val(),20+val(),20+val(),20+val()]
	        threshold = [16,16,16,16,16,16,16,16,16,16,16,16]
		node = [temp[0],temp[1],temp[2],temp[3],temp[4],temp[5],temp[6],temp[7],temp[8],temp[9],temp[10],temp[11]]
		cur.execute("INSERT INTO `heating`.`node_data` (`Node`, `Temperature`, `Threshold`) VALUES ('%.0f', '%.1f', '%.1f');" % (i, node[i], threshold[i]))

for number in range(20):
	temp = [20+val(),21+val(),22+val(),23+val(),24+val(),25+val(),26+val(),27+val(),28+val(),29+val(),30+val(),31+val(),32+val()]
	threshold = [16,16,16,16,16,16,16,16,16,16,16,16]
	#temp = [21,22,23,24,25,26,27,28,29,30,31,32]
	node = [temp[0],temp[1],temp[2],temp[3],temp[4],temp[5],temp[6],temp[7],temp[8],temp[9],temp[10],temp[11]]

	for i in range(12):
#		cur.execute("UPDATE `heating`.`node_data` SET (`Node`='%.0f', `Temperature`='%.1f', `Threshold`='%.1f') WHERE `Node`='%.0f';" % (i, node[i], threshold[i], i))
		cur.execute("UPDATE heating.node_data SET Node='%.0f', Temperature='%.1f', Threshold='%.1f' WHERE Node='%.0f';" % (i, node[i], threshold[i], i))
                print "Found match with node: %.0f, Inserted into mysql database:" % i
                print "         Node: %.0f Temperature: %.1f Threshold: %.1f\n" % (i, node[i], threshold[i])

	cur.execute("SELECT * FROM node_data")
	print "Database:"
	for row in cur.fetchall():
	        print "		Node: %.0f Temperature: %.1f Threshold: %.1f" % (row[0], row[1], row[2])

	data = {}
	data['time'] = time.strftime("%d/%m/%Y %H:%M:%S") # time

	for x in range(12):
	        data['node'+str(x)] = str(node[x]) # degs C

	entry = spr_client.InsertRow(data, spreadsheet_key, worksheet_id)
	print "Inserting into google docs: "
	print "		" + str(entry)

#        if isinstance(entry, gdata.spreadsheet.SpreadsheetsList):
#                print "Insert row succeeded."
#        else:
#                print "Insert row failed."
