#!/usr/bin/python
'''
Update from a zipfile given a URL
'''

__author__    = "Patrick Butler <pbutler@killertux.org>"
__version__   = "$Revision: 31 $"
__copyright__ = "Copyright 2005,2006 Patrick Butler"
__license__   = "GPL Version 2"

import wowaddon
import re
import os
import urllib
import time;

class Plugin(wowaddon.Plugin):
	def __init__(self, updater, args):
		wowaddon.Plugin.__init__(self, updater, args)
		if (args[0] == ""):
			raise "Need id"
		self.id = args[0]
		self.name = self.id
		self.type = "Remote"
		self.link = self.id
		zname = self.id
		zname = self.id.replace('.zip', '')
		zname = re.sub("[^A-Za-z0-9]", "", zname)[-12:];
		zname += str(int(time.time())) + ".zip"
		self.zipfilename = zname

	def getname(self):
		return self.name

	def isuptodate(self):
		return False

	def getinfo(self):
		pass;

	def help():
		return """
This should be a web URL for the mod you want to install
"""
	help = staticmethod(help)

	def argdesc():
		return [ { 
			'title' : 'Remote Source',
			'type' : 'str',
			'desc' : 'Please enter the URL for the zipfile of the mod you want to use', }]
	argdesc = staticmethod(argdesc)

wowaddon.addModType("Remote", Plugin)

