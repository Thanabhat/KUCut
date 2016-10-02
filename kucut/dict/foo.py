#!/usr/bin/python

import sys

tmp = []
lines = sys.__stdin__.readlines()
for line in map(str.strip,lines):
	if line not in tmp:
		tmp.append(line)

for word in tmp:
	print word
	
