#!/usr/bin/python
'''
Plugin for updating NurfedUI
'''

__author__    = "Patrick Butler <pbutler@killertux.org>"
__version__   = "$Revision: 31 $"
__copyright__ = "Copyright 2005,2006 Patrick Butler"
__license__   = "GPL Version 2"

import wowaddon
import urllib
import urllib2
import re
import os
import shutil

class Plugin(wowaddon.Plugin):
	def __init__(self, updater, args):
		wowaddon.Plugin.__init__(self, updater, args)
		if (id == ""):
			raise "Need id"
		self.id =  'nurfed'
		self.type = "Nurfed UI"

	def getinfo(self):
		if self.timemutex(60):
			return
		

		self.out("Checking mod NurfedUI")
		try:
			data = urllib.urlopen("http://www.nurfedui.net").read()
			version = re.compile("(?is)<font[^>]*>Updated:</font>\s*([^<]+?)\s*</b>").search(data).group(1)
			#print version
		except IOError:
			raise wowaddon.DownloadError

		
		self.name = 'NurfedUI '  + wowaddon.cleanuphtml(version)
		self.link = 'http://www.nurfedui.net/download.php?file=nurfedui.zip'
		self.newversion = version
		self.zipfilename = 'nurfedui.zip'
		return self.link, self.newversion, self.zipfilename

	def update(self):
		zipdir = self.getoption('zipdir')

		if self.link == "":
			self.getinfo();
		#print self.link;
		name = self.id+".zip"
		self.out("%s (%s)" % (self.link, name))
		zipfile = os.path.join(zipdir, self.zipfilename)

		link = self.link
		link = link.replace(" ", "%20")

		self.out("Downloading NurfedUI...")
		try:
			req =  urllib2.Request(self.link)
			req.add_header("Referer", "http://www.nurfedui.net")
			fpage = urllib2.urlopen(req, 'download=Download')

			file = open(zipfile, "wb")
			file.write(fpage.read())
			file.close()
		except IOError, e:
			raise DownloadError, e;
		self.zipfile = zipfile
		self.out("Downloading NurfedUI... done")
		return

	def postcopy(self):
		ifacedir = os.path.join(self.getoption('wowdir'), "Interface")
		wowaddon.nopatch(ifacedir, self.outfiles);


	def help():
                return ""

	def argdesc():
		return None
				 
	help = staticmethod(help)
	argdesc = staticmethod(argdesc)

wowaddon.addModType("Nurfed UI", Plugin)


if __name__ == "__main__":
	p = Plugin(None, [])
	print p.getinfo()


