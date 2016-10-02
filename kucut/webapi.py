#-*- coding:utf-8 -*-

from simple_kucut_wrapper import SimpleKucutWrapper as Kucut
import cherrypy
import re
try:
    import json
    json.dumps
except:
    import simplejson as json 
    
kucut = Kucut()

class KucutWebApi(object):
    def index(self, text):
        lines = re.split("[\r\n]", text)
        result = kucut.tokenize(lines)
        return json.dumps(result)
    index.exposed = True
    
cherrypy.server.socket_port = 8089
cherrypy.quickstart(KucutWebApi())