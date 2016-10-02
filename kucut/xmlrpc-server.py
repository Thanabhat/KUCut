#! /usr/bin/python
#-*- coding:utf8 -*-

from wordcut import *

import os.path, sys
import SimpleXMLRPCServer

global seq

def init():
    ## initial step ##
    HOME = './'
    HOME = os.path.abspath(HOME)

    lexicon_file = os.path.join(HOME,'dict/lexicon.txt')
    syllable_file = os.path.join(HOME,'dict/syllable.txt')
    database_file = os.path.join(HOME,'corpus.db')

    lexiconDict = Dictionary(lexicon_file)
    syllableDict = Dictionary(syllable_file)

    global seg

    seg = Segmentation(syllable = syllableDict,
        lexicon = lexiconDict,
        quiet = True,
        database = database_file,
        blank = '_',
        home = HOME)

    prohibit_file = os.path.join(HOME,'dict/prohibit.txt')
    seg.loadProhibitPattern(prohibit_file)
    ## end of initial step ##

def cutstring(text):
    global seg

    isuni = False

    ## check unicode and convert to cp874
    if isinstance(text,unicode):
        isuni = True
        text = text.encode('cp874')

    ## process segmentation
    results,ambiguous_list = seg.tokenize(text.split('\n'), style='Normal', space=True)

    ## reformat output
    outputs = []
    for result in results:
        for t in result[1]:
            tmp = ''
            for r in t[0]:
                tmp += r + ' '

            if isuni: tmp = tmp.decode('cp874')

            outputs.append(tmp.strip())

    return outputs

def cutsentence(text):
    import re

    if re.search('\w',text): # don't process text which contains alpha-numeric
        return text

    global seg
    isuni = False

    ## check unicode and convert to cp874
    if isinstance(text,unicode):
        isuni = True
        text = text.encode('cp874')
    else:
        try:
            text = text.decode('utf8').encode('cp874')
        except Exception,e:
            pass

    ## process segmentation
    results,ambiguous_list = seg.tokenize(text.split('\n'), style='Normal', space=True)

    ## reformat output
    outputs = []
    for result in results:
        for t in result[1]:
            tmp = ''
            for r in t[0]:
                tmp += r + ' '

            if isuni: tmp = tmp.decode('cp874')

            outputs.append(tmp.strip())

    return ' ' + outputs[0]

def hello(name):
    return 'hello' + name

port = 8089

if len(sys.argv) == 1:
    print 'default port 8089 is used'
else:
    try:
        port = int(sys.argv[1])
    except ValueError,e:
        print 'invalid port'
        sys.exit(1)

## init wordcut object
init()

server = SimpleXMLRPCServer.SimpleXMLRPCServer(('localhost',port))
server.register_function(cutstring)
server.register_function(cutsentence)
server.register_function(hello)
server.register_introspection_functions()

print 'server is started at port %d' % (port)

## start server
server.serve_forever()
