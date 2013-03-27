#!/usr/bin/env python

import select, socket, sys, json

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

conn1 = None
conn2 = None

print "WAITING"

s.bind(('', int(sys.argv[1])))
s.listen(1)
conn1, addr1 = s.accept()
s.listen(1)
conn2, addr2 = s.accept()

conn1.setblocking(0)
conn2.setblocking(0)

msg = json.dumps({"type": "go"})
print "GO"
conn1.sendall(msg + "\n")
conn2.sendall(msg + "\n")

inputs = [conn1, conn2]

while True:
	readl, writel, exceptl = select.select(inputs, [], inputs)
	from_c = None
	to_c = None
	for s in readl:
		if(s == conn1):
			from_c = conn1
			to_c = conn2
		elif(s == conn2):
			from_c = conn2
			to_c = conn1
		else:
			continue
		print "SENDING"
		data = from_c.recv(1024)
		try:
			to_c.sendall(data)
		except:
			print "ERROR! QUTTING!"
			sys.exit(-1)
print "Quitting."
