#!/usr/bin/python
'''
Update from a local file on the hard drive
'''

__author__    = "Patrick Butler <pbutler@killertux.org>"
__version__   = "$Revision: 31 $"
__copyright__ = "Copyright 2005,2006 Patrick Butler"
__license__   = "GPL Version 2"

import wowaddon
import re
import os
import urllib
import shutil

class Plugin(wowaddon.Plugin):
	def __init__(self, updater, args):
		wowaddon.Plugin.__init__(self, updater, args)
		if (args[0] == ""):
			raise "Need id"
		self.id =  args[0]
		self.name = "%s" % id
		self.type = "Local"
		self.link = ""

	def getname(self):
		return self.name

	def isuptodate(self):
		return False


	def update(self):
		zipdir = self.getoption("zipdir")
		zipfile = os.path.join(zipdir,  os.path.basename(self.id))

		if os.path.exists(self.zipfile):
			os.unlink(self.zipfile);
			self.zipfile = ""

		shutil.copy(self.id, zipfile)
		self.zipfile = zipfile
		return

	def getinfo(self):
		print "BAH shouldn't be called"

	def help():
		return """
The argument should be a locale filename for a zipfile containing the mod you want installed
"""
	def argdesc():
		return [ {	'title' : 'Local File', 
				'desc'  : 'Please the location of a zip file to update from',
				'type'  : 'file', } ]
	help = staticmethod(help)
	argdesc = staticmethod(argdesc)

wowaddon.addModType("Local", Plugin)

