import pickle
'''
Used for testing files
'''
__author__  = "Patrick Butler <pbutler@killertux.org>"
__version__ = "$Revision: 31 $"
__copyright = "Copyright 2005,2006 Patrick Butler"
__license__ = "GPL Version 2"

import os
import curses
import wowaddon
import uiwownet
import ctmod

class Test:
	def __init__(self):
		self.options = {	'zipdir'   : 'zips',
					'ifacedir' : 'Interface' 
				}
		if( not os.path.exists("zips") ):
			os.makedirs("zips");
		self.mods = []
		self.mods.append( ctmod.Plugin(self, "CT_MasterMod")  )
		print self.mods
		for m in self.mods:
			if not m.isuptodate():
				print m.version
				print "updating"
				m.update()
				m.unzip()
				m.copy()
			else:	
				print "nothing to do"
			print m.outfiles
			print m.getname()

	def log(self,str):
		print str

	def out2(self,str):
		print "**", str

	def out(self,str, nolog=0):
		print "*", str

	def getoption(self, name):
		return self.options[name]

	def setoption(self, name, val):
		self.options[name] = val
	#mod
#if (not  mod.isuptodate() ):
#	update(:wq
print ctmod.Plugin.help();
#t = Test()
#print wowaddon.getModTypes()

