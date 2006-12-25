#!/usr/bin/python
'''
Plugin for updating from www.wowinterface.com
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
		self.type = "WoWInterface"

	def getinfo(self):
		if self.timemutex(60):
			return
		

		self.out("Checking mod WOWIF:%s" % (self.id))
		try:
			data = urllib.urlopen("http://www.wowinterface.com/downloads/fileinfo.php?id=" + self.id).read()
			#name = re.compile("(?is)<td[^>]*><b>Name:</b></td>[^<]*<td[^>]*>([^<]+)</td>").search(data).group(1)
			name = re.compile("(?is)<td[^>]*><b>Name:</b></td>[^<]*<td[^>]*><a href=[^>]+>([^<]+)</a>").search(data).group(1)
			#print name
			version = re.compile("(?is)<td[^>]*><b>Version:</b></td>[^<]*<td[^>]*>([^<]+)</td>").search(data).group(1)
			#print version
		except IOError:
			raise wowaddon.DownloadError

		
		self.name = wowaddon.cleanuphtml(name) + " " + wowaddon.cleanuphtml(version)
		self.link = 'http://www.wowinterface.com/downloads/dl.php?id=' + str(self.id)
		self.newversion = version
		self.zipfilename = re.sub('[^-_a-zA-Z0-9]', '', self.name.strip().replace(' ', '_')) + ".zip"
		return self.link, self.newversion, self.zipfilename

	def postcopy(self):
		ifacedir = os.path.join(self.getoption('wowdir'), "Interface")
		wowaddon.nopatch(ifacedir, self.outfiles);


	def help():
                return ""

	def search(text):
		go = True
		ret = []
		datere = re.compile("(\d+-\d+-\d+)");
		comped = re.compile("(?is)[\r\n]+<a href=\"fileinfo.php?[^\"]*id=(\d+)[^\"]*\"[^>]*>([^<]+)</a>(.*?)</tr>")
		filesre = re.compile("Showing files (\d+) to (\d+) of (\d+)");
		page = 1
		searchid = None
		while go:
			go = False
			textq = urllib.quote_plus(text)
			posta =	{ "s"		: '',
				  "searchcat"	: "all",
				  "searchdate"	: "-1",
				  "sb"		: "filename",
				  "so"		: "asc",
				  "showdetails"	: "0",
				  "action"	: "search",
				  "searchtext"	: textq }
			if page > 1:
				posta['action'] = 'showresults'
				posta['page'] = page
				posta['searchid'] = searchid

			post = urllib.urlencode(posta)
			try:
				data = urllib.urlopen("http://www.wowinterface.com/downloads/search.php", post).read()
			except IOError:
				raise wowaddon.DownloadError
	
			match = comped.search(data, 0)

			while match != None:
				id = match.group(1)
				name = match.group(2)
				rest = match.group(3) 

				date = ""
				delim = "</a>"
				try: 
					date = datere.search(rest).group(1)
				except AttributeError:
					raise wowaddon.ParseError
				
				name = wowaddon.cleanuphtml(name)
				ret.append( (id, name + " -- " + date) )
				match = comped.search(data, match.end() )

			go = False
			match = filesre.search(data)
			if match != None:
				(start, stop, end) = match.groups()
				if int(stop) < int(end):
					go = True
					page += 1
					searchid = re.search('searchid=(\d+)', data).group(1)
				#print (start, stop, end), page, searchid


		return ret

	def argdesc():
		return [ {	'title' : 'WoW Interface.com',
				'desc'  : 'Please enter the search string for the mod',
				'type'  : 'func',
				'type1' : 'str',
				'desc2' : 'Choose your mod',
				'func'  : Plugin.search } ]
				
				 
	help = staticmethod(help)
	search = staticmethod(search)
	argdesc = staticmethod(argdesc)

wowaddon.addModType("WoWInterface.com", Plugin)


if __name__ == "__main__":
	list = Plugin.search('lootlink')
	print len(list)
	print list
	p = Plugin(None, [ list[-1][0] ] )
	print p.getinfo()


