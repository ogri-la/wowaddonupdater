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
		(self.id, self.dname) = args[0].split('/', 1)
		#print (self.id, self.dname)
		self.type = "Curse"

	def getinfo(self):
		#if self.timemutex(60):
		#	return
		

		self.out("Checking mod %s:%s" % (self.id, self.dname))
		try:
			data = urllib.urlopen("http://www.curse-gaming.com/en/files/details/" + self.id + "/" + self.dname  + "/" ).read()
			name = re.compile("<h1>(.*?)</h1>").search(data).group(1)
		except IOError:
			raise wowaddon.DownloadError

		#matches = re.compile("<a href=\"(/../files/downloads/(\d+)/)\"").findall(data, re.I and re.S)
		matches = re.compile("<a href=\"(/../files/downloads/(\d+)/)\"[^>]+>([^<]+)<").findall(data, re.I and re.S)
		#self.out(str(matches))
		if matches == None or matches == []:
			self.out("No files found to dwnload: %s" % self.id)
			raise wowaddon.ParseError
			
		bestid = -1
		bestlink = ""
		bestvername = ""
		for m in matches:
			link, downid, vername = m
			downid = int(downid)
			if downid > bestid:
				bestid = downid
				bestlink = link
				bestvername = vername
		
		if bestid < 1: 
			self.out("Failed to parse download URL for mod CURSE:%s:%s" % (self.id, self.dname) )
			raise wowaddon.ParseError
		self.log("Bestlink: %s" %bestlink)
		dlpagelink = "http://wow.curse-gaming.com" + bestlink

		try:
			dlpage = urllib.urlopen(dlpagelink).read()
		except IOError:
			raise wowaddon.DownloadError("Couldn't get dlpage")
		dlpage = re.search("(?is)<ul\s+id=\"mirrorlist\">(.*?)</ul>", dlpage).group(1)
		matches = re.search("(?ism)<li class=\"(auto|row.?)\"><a\s+href=\"([^\"]+?)\">" , dlpage)

		if matches == None:
			raise wowaddon.ParseError

		link = matches.group(2)
		self.name = wowaddon.cleanuphtml(name) + " " + wowaddon.cleanuphtml(bestvername)
		self.link = link
		self.newversion = bestid
		self.zipfilename = re.sub('[^-_a-zA-Z0-9]', '', self.name.strip().replace(' ', '_')) + ".zip"
		self.log("Curses %s,%s,%s" %(self.link, self.newversion, self.zipfilename))
		return self.link, self.newversion, self.zipfilename

	def postcopy(self):
		ifacedir = os.path.join(self.getoption('wowdir'), "Interface")
		wowaddon.nopatch(ifacedir, self.outfiles);


	def help():
                return ""

	def search(text):
		ret = []
		textq = urllib.quote_plus(text)
		post = urllib.urlencode({ "q"		: text,
					  "q_labels"	: "1",
					  "cat"		: "1" })
		try:
			data = urllib.urlopen("http://wow.curse-gaming.com/en/files/search/?" + post).read()
		except IOError:
			raise wowaddon.DownloadError
		
		datere = re.compile("(\d+/\d+/\d+)");
		comped = re.compile("(?is)span><a href=\"/../files/details/(\d+/[^\"]+)/\"[^>]+>(.*?)</tr>")
	
		match = comped.search(data, 0)

		while match != None:
			id = match.group(1)
			rest = match.group(2) 
			
			name = ""
			date = ""
			delim = "</a>"
			if rest.find(delim) > -1:
				(name, rest) = rest.split(delim, 1);
				name = name
			else:
				raise wowaddon.ParseError
			try: 
				date = datere.search(rest).group(1)
			except AttributeError:
				raise wowaddon.ParseError
				
			name = wowaddon.cleanuphtml(name)
			ret.append( (id, name + " -- " + date) )
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


if __name__ == "__main__":
	list = Plugin.search('smurfy')
	print list
	p = Plugin(None, [ list[0][0] ] )
	print p.getinfo()


