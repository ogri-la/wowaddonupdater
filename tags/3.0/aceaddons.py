#!/usr/bin/python
'''
Update a CTMod Addon
'''

__author__    = "Patrick Butler <pbutler@killertux.org>"
__version__   = "$Revision: 31 $"
__copyright__ = "Copyright 2005,2006 Patrick Butler"
__license__   = "GPL Version 2"

import wowaddon
import re
import os
import urllib

class Plugin(wowaddon.Plugin):
	urls = [ 'http://www.wowace.com/files/', 'http://grid.13th-floor.org/wowace/']
	iurl = 0
	def __init__(self, updater, args):
		wowaddon.Plugin.__init__(self, updater, args)
		if (args[0] == ""):
			raise "Need id"
		self.id = args[0].strip();
		self.name = self.id
		self.type = "ACE"
	
	def getinfo(self):
		if self.timemutex(60):
			return
		self.out("Checking ACE:%s version..." % self.id )
		try:
			data = multiurlopen("")
		except IOError, e:
			raise wowaddon.DownloadError(e)
		rows = re.split("<tr>", data)
		version = ""
		for r in rows:
			match = re.search(r"(?is)<td><a href=\"([^\"]+)\">"+self.id+r"</a></td><td>(r\d+)</td>.*?(\d+-\d+-\d+)", r)
			if match != None:
				link = match.group(1)
				version =  match.group(2)

		if(version == ""):
			raise wowaddon.ParseError

		self.newversion = version
		self.link = Plugin.urls[Plugin.iurl] + link
		self.name = self.id + " " + self.newversion
		self.zipfilename = self.id + ".zip"
		return self.link, self.newversion, self.zipfilename

	def help():
		return """
"""
	def search():
		ret = []

		try:
			data = multiurlopen("")
		except IOError:
			raise wowaddon.DownloadError

		rows = re.split("<tr[^>]*>", data)
		for r in rows:
			match = re.search(r"<td><a href=\"([^\"]+)\">([^<]+)</a></td><td>(r\d+)</td>.*?(\d+-\d+-\d+)", r, re.I and re.S)
			if match != None: 
				id = match.group(2)
				name = match.group(2) + ' ' +match.group(3) + ' -- ' + match.group(4)
				ret.append( (id, name) )
		if ret == []:
			raise wowaddon.ParseError
		return ret


			
	def argdesc():
		return [ { 
			'title' : 'Ace Addons', 
			'type' : 'func', 
			'type1' : 'None', 
			'func' : Plugin.search,
			'desc' : 'The following page will allow you to install the ACE Addons of your choice.\n Some mods make use of a second mod (i.e. Autobar and Autobarconfig) please make sure you install both if you wish to get full functionality',
			'desc2' : 'Which Ace Addon would you like to install?' } ];
	help = staticmethod(help)
	search = staticmethod(search)
	argdesc = staticmethod(argdesc)

def multiurlopen(dir):
	laste = None
	for i in range(len(Plugin.urls)):
		iu =  (i + Plugin.iurl) % len(Plugin.urls)
		try:
			data = urllib.urlopen(Plugin.urls[iu]+dir).read()	
			#print "Got from %s" % Plugin.urls[iu]+dir
			if i > 0:
				Plugin.iurl = iu
			return data
		except IOError, e:
			laste = e

	raise IOError, laste
	return None

wowaddon.addModType("Ace Addons", Plugin)

if __name__ == "__main__":
	list = Plugin.search()
	print list[:5]
	p = Plugin( None,  [ list[0][0] ] )
	print p.getinfo()

