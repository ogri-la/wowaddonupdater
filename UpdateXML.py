#!/usr/bin/python
'''
This little gem parses the XML file that describes where to download the 
updates from/
'''

__author__    = "Patrick Butler <pbutler@killertux.org>"
__version__   = "$Revision: 31 $"
__copyright__ = "Copyright 2005,2006 Patrick Butler"
__license__   = "GPL Version 2"

import sys

import xml
from xml.dom.minidom import parse, parseString
from xml.dom import minidom, Node

def readFileNode(file):
	ret = { 'source': None, 'dir': None, 'name': None, 'md5': None, 'version' : -1 }
	for node in  file.childNodes:
		if node.nodeType == Node.ELEMENT_NODE and node.nodeName in ret.keys():
			if node.childNodes == []:
				continue
			if node.childNodes[0].nodeType == Node.TEXT_NODE:
				ret[node.nodeName] = node.childNodes[0].nodeValue
				if node.nodeName == 'version':
					ret[node.nodeName] = float( ret[node.nodeName] )
	return ret


def walkNodes(doc):
	ret = {}
	listFiles = doc.getElementsByTagName('files')
	#if no root node or no file nodes
	if listFiles == None:
		return None
	
 	for files in listFiles:
 		for f in  files.childNodes:
			data = readFileNode(f)
			key = data['name']
			if key == None:
				continue
			if data['dir'] != None:
				key = data['dir'] + "/" + key
			ret[key] = data
	return ret

def parse(s): 
	try : 		
		doc = minidom.parse(s)
		return walkNodes(doc)
	except xml.parsers.expat.ExpatError:
		return None

def parseString(fn): 
	try:			
		doc = minidom.parseString(fn)
		return walkNodes(doc)
	except xml.parsers.expat.ExpatError:
		return None


if __name__ == '__main__':
	s ='''
<files>
  <file>
    <dir></dir>
    <name>test.py</name>
    <source>http://nowhere.com/test.py</source>
    <md5>blahbalh</md5>
    <version>1.1</version>
  </file>
</files>
'''
	if len(sys.argv) > 1:
		print parse(sys.argv[1])
	else:
		print parseString(s)
