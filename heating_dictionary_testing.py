data_old = {'0':20,'1':21,'2':22}
data_new = {'0':19,'1':22,'2':22}
nodes = [0,1,2]

def get_diff(node):
	global data_old,data_new
	old_temp = data_old[str(node)]
	new_temp = data_new[str(node)]
	if old_temp != new_temp:
		if float(old_temp) > float(new_temp):
			diff_type = ">"
			diff = float(old_temp) - float(new_temp)
		if float(old_temp) < float(new_temp):
        	        diff_type = "<"
			diff = float(new_temp) - float(old_temp)
		data_old[str(node)] = data_new[str(node)]
		return True,node,new_temp,diff_type,diff

for i in range(1):
	for node in nodes:
		diff = get_diff(node)
		if diff is not None:
			if diff[3] == "<":
				print "%s increased by: %.1f" % (node,diff[4]) + u"\u2103"
			if diff[3] == ">":
		                print "%s decreased by: %.1f" % (node,diff[4]) + u"\u2103"
		else:
			print "%s no change" % (node)
