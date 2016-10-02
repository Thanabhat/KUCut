#!/usr/bin/python

import sys

for line in sys.__stdin__.readlines():
    print ''.join(line.strip().split()).replace('_','')
