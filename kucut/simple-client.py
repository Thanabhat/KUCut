#!/usr/bin/python

import sys
from xmlrpclib import ServerProxy

server = ServerProxy(uri="http://localhost:8089",encoding='cp874')

text = sys.argv[1]

try:
	text = text.decode('utf8').encode('cp874')
except Exception,e:
	pass

tmp = []
for token in text.split():
	result = server.cutsentence(text)
	tmp.append(result)
print ' _ '.join(tmp)
