#!/usr/bin/python
'''
Plugin for updating from http://ui.worldofwar.net
'''

__author__    = "Patrick Butler <pbutler@killertux.org>"
__version__   = "$Revision: 31 $"
__copyright__ = "Copyright 2005,2006 Patrick Butler"
__license__   = "GPL Version 2"

import wowaddon
import os
import urllib
import re

class Plugin(wowaddon.Plugin):
	def __init__(self, updater, args):
		wowaddon.Plugin.__init__(self, updater, args)
		if (args[0] == ""):
			raise "Need id"
		self.id = args[0]
		self.type = "uiwownet"
		self.link = ""


	def getinfo(self):
		if self.timemutex(60):
			return
		
		
		self.out("Checking mod %s" % self.id)
		try: 
			data = urllib.urlopen("http://ui.worldofwar.net/download.php?dbtable=maps&id="+str(self.id)+"&g=1").read()
		except IOError, e:
			raise wowaddon.DownloadError, e
		#print "ha"
		match = re.search("<!--MET5A HTTP-EQUI5V5=\"Refresh\" CONTENT=\"\d+; URL=(.*?)\"-->", data, re.I and re.S)

		if match == None:
			self.out("Failed to parse download URL for mod %s" % self.id)
			raise wowaddon.ParseError
		link = match.group(1)

		zname = re.search(r".*/\d*(.*?)\.zip$", link).group(1)
		zname = zname.replace("%20", "_")
		name =  zname
		name = name.replace("_", " ")


		self.name = name
		self.newversion = link
		self.link = link
		self.zipfilename = zname+".zip"
		return self.name, self.link, self.zipfilename

	def postcopy(self):
		ifacedir = os.path.join(self.getoption('wowdir'), "Interface")
		wowaddon.nopatch(ifacedir, self.outfiles);

	def help():
		return """
For the argument, goto http://www.curse-gaming.com/mod.php ;  search for the mod you want and click on the link for it.  The address should be something like \"http://www.curse-gaming.com/mod.php?addid=694\".  Where the number at the end is the mod id, for the mod you want.
"""

	def search(text):
		ret = []
		textq = urllib.quote_plus(text)
		try:
			data = urllib.urlopen("http://ui.worldofwar.net/listuis.php?searchtext=" +textq).read()
		except IOError, e:
			raise wowaddon.DownloadError, e 

		datere = re.compile("(\d+/\d+/\d+)")
		comped = re.compile("(?is)<a href=\"[./]*ui.php\?id=(\d+)\">(.*?)</a>(.*?)</tr>")
	
		match = comped.search(data, 0)
		while match != None: 
			(id, name, rest) = match.groups() 
			date = datere.search(rest).group(1)
			ret.append( (id, name + " -- " + date) ) 
			match = comped.search(data, match.end() )
		
		return ret

	def argdesc():
		return [ {	'title' : 'UI.WorldOfWar.net',
				'desc'  : 'Please enter the search string for the mod',
				'type'  : 'func',
				'type1' : 'str',
				'desc2' : 'Choose your mod',
				'func'  : Plugin.search } ]
	argdesc = staticmethod(argdesc)
				

	help = staticmethod(help)
	search = staticmethod(search)

wowaddon.addModType("UI.WorldofWar.Net", Plugin);


if __name__ == "__main__":
        list = Plugin.search('sw stats')
        print list
        p = Plugin(None, [ list[0][0] ] )
        print p.getinfo()


