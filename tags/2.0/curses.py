#!/usr/bin/python
'''
Plugin for updating from www.curse-gaming.com
'''

__author__    = "Patrick Butler <pbutler@killertux.org>"
__version__   = "$Revision: 31 $"
__copyright__ = "Copyright 2005,2006 Patrick Butler"
__license__   = "GPL Version 2"

import wowaddon
import urllib
import re
import os
import shutil

class Plugin(wowaddon.Plugin):
	def __init__(self, updater, args):
		wowaddon.Plugin.__init__(self, updater, args)
		if (id == ""):
			raise "Need id"
		self.id = args[0]
		self.type = "Curse"

	def getinfo(self):
		if self.timemutex(60):
			return
		
		id = self.id
		self.out("Checking mod %s" % id)
		try:
			data = urllib.urlopen("http://www.curse-gaming.com/en/" + str(id)).read()
			name = re.compile("<h1>(.*?)</h1>").search(data).group(1)
		except IOError:
			raise wowaddon.DownloadError

		matches = re.compile("<a href=\"(download-(\d+).html)\">").findall(data, re.I and re.S)
		self.out(str(matches))
		if matches == None:
			raise wowaddon.ParseError
			
		bestid = -1
		bestlink = ""
		for m in matches:
			link,downid = m
			if(downid > bestlink):
				bestid = downid
				bestlink = link
			self.out(link + " " + downid)
			#print link, downid
		
		if bestid < 1: 
			self.out("Failed to parse download URL for mod CURSE:%s" % id)
			raise wowaddon.ParseError
		
		dlpagelink = "http://www.curse-gaming.com/en/wow/download-" + str(bestid) + ".html"
		try:
			dlpage = urllib.urlopen(dlpagelink).read()
		except IOError:
			raise wowaddon.DownloadError("Couldn't get dlpage")
		
		matches = re.search("(?ism)<thead>.*?Links.*?</thead>.*?<tbody>.*?<a\s+href=\"(.*?)\">.*?</tbody>" , dlpage)

		if matches == None:
			raise wowaddon.ParseError

		link = matches.group(1)
		self.name = wowaddon.cleanuphtml(name)
		self.link = link
		self.newversion = bestid
		self.zipfilename = re.sub('[^A-Za-z0-9_]', '', self.name.strip().replace(' ', '_')) + ".zip"
		#print self.zipfilename 

	def postcopy(self):
		ifacedir = os.path.join(self.getoption('wowdir'), "Interface")
		wowaddon.nopatch(ifacedir, self.outfiles);


	def help():
                return """
For the argument, goto http://ui.worldofwar.net/ ;  search for the mod you want and click on the link for it.  The address should be something like \"http://ui.worldofwar.net/ui.php?id=120\".  Where the number at the end is the mod id, for the mod you want.
"""

	def search(text):
		ret = []
		textq = urllib.quote_plus(text)
		post = urllib.urlencode({ "searchtext" : text,
					  "type"       : "wow",
					  "submit"     : "Search" })
		try:
			data = urllib.urlopen("http://www.curse-gaming.com/en/search.html" , post).read()
		except IOError:
			raise wowaddon.DownloadError

		comped = re.compile("<a href=\"(wow/addons-[^\"]+)\">(.*?)</td>", re.I & re.S)
	
		match = comped.search(data, 0)
		while match != None:
			id = match.group(1)
			name = match.group(2) 
			delim = "</a><br />"
			if name.find(delim) > -1:
				(name, desc) = name.split(delim, 1);
				name = name + " -- " + desc
			else:
				name = name[:name.find("</a>")]
			name = wowaddon.cleanuphtml(name)
			ret.append( (id, name) )
			match = comped.search(data, match.end() )

		return ret

	def argdesc():
		return [ {	'title' : 'Curse Gaming',
				'desc'  : 'Please enter the search string for the mod',
				'type'  : 'func',
				'type1' : 'str',
				'desc2' : 'Choose your mod',
				'func'  : Plugin.search } ]
				
				 
	help = staticmethod(help)
	search = staticmethod(search)
	argdesc = staticmethod(argdesc)

wowaddon.addModType("Curse Gaming", Plugin)



