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
	def __init__(self, updater, args):
		wowaddon.Plugin.__init__(self, updater, args)
		if (args[0] == ""):
			raise "Need id"
		self.id = args[0].strip();
		self.name = self.id
		self.type = "CTMod"
	
	def getinfo(self):
		if self.timemutex(60):
			return
		self.out("Checking CTMod:%s version..." % self.id )
		try:
			data = urllib.urlopen("http://www.ctmod.net/downloads.ct").read()
		except IOError, e:
			raise wowaddon.DownloadError(e)
		rows = re.split("<tr>", data)
		version = ""
		for r in rows:
			match = re.search(r"<b>\s*"+self.id + r"\s*</b>\s*(v[0-9.]+\s*\(\d+\))", r, re.I and re.S)
			if match != None:
				version =  match.group(1)
		if(version == ""):
			raise wowaddon.ParseError

		self.newversion = version
		self.link = "http://www.ctmod.net/downloads.ct?a=download&m=" + self.id
		self.name = self.id + " " + self.newversion
		self.zipfilename = self.id + ".zip"

	def help():
		return """
You must download each mod separately, and if you download one then you probably need to get CT_MasterMod.  The argument may be obtained at http://www.ctmod.net/downloads.ct .  Use the name of the mod, paying attention to the capitalization eg.  CT_MasterMod, CT_BottomBar, CT_BagMod
"""
	def search():
		ret = []
		try:
			data = urllib.urlopen("http://www.ctmod.net/downloads.ct").read()
		except IOError:
			raise wowaddon.DownloadError

		rows = re.split("<tr[^>]*>", data)
		for r in rows:
			match = re.search(r"<b>\s*([^<]*?)</b>\s*(v[0-9.]+\s*\(\d+\))", r, re.I and re.S)
			if match != None: 
				ret.append(match.group(1) )
		if ret == []:
			raise wowaddon.ParseError
		return ret

	def argdesc():
		return [ { 
			'title' : 'CTMod', 
			'type' : 'func', 
			'type1' : 'None', 
			'func' : Plugin.search,
			'desc' : 'The following page will allow you to install the CTMods of your choice.\nPlease make sure to install CT_Mastermod with whatever else you install' ,
			'desc2' : 'Which CTMod module would you like to install?' } ];
	help = staticmethod(help)
	search = staticmethod(search)
	argdesc = staticmethod(argdesc)

wowaddon.addModType("CTMod", Plugin)

