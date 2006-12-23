#!/usr/bin/pythonw
'''
This is the heart and brains of the WoW Updater Addon.  In theory it can
be used to create a CLI or GUI version.  Since only a GUI version is
useful ATM there is no CLI version written
'''

__author__    = "Patrick Butler <pbutler@killertux.org>"
__version__   = "$Revision: 31 $"
__copyright__ = "Copyright 2005,2006 Patrick Butler"
__license__   = "GPL Version 2"

import platform
import urllib
import sys
import re
import shutil
import os
import mutex
import pickle


################################
# AddOn Plugins
################################
import wowaddon
import uiwownet
import curses
import cosmos
import ctmod 
import local
import remote

from wowaddon import ParseError, DownloadError

class VerCheckError(Exception): pass
class CleanError(Exception): pass
class UnzipError(Exception): pass
class CopyError(Exception): pass
class UpdaterError(Exception): pass

schemaver = 3

class Updater:
	def __init__(self):
		self.defaults = {	'zipdir'    : 'zips', 
					'mods'      : None,
					'release'   : '-1',
					'version'   : schemaver,
					'zipdir'    : 'zips',
					#'ifacedir'  : 'Interface',
				}
		self.config = {}
		self.loglines = []
		self.errors = []
		self.progmutex = mutex.mutex()
		self.startmutex = mutex.mutex()

		#keep us from doing anything until we are done setting up
		self.startmutex.testandset()

		self.modspkl = "mods.pkl"
		self.confpkl = "config.pkl"
		self.filepkl = "files.pkl"
		if(platform.system() == "Windows"):
			self.defaults['wowdir'] = r"C:\Program Files\World of Warcraft"
		elif(platform.system() == "Darwin"):
			self.defaults['wowdir'] = "/Applications/World of Warcraft"
			#Work in the .app dir
			workingdir = os.path.join(os.path.dirname(sys.argv[0]), "working")
			if(not os.path.exists(workingdir)) :
				os.makedirs(workingdir)
			os.chdir(workingdir)
			#Store config file in a sane place on OSX
			confdir = os.path.join(os.environ['HOME'], "Library", "Preferences", "org.killertux.wowaddonupdater")
			if(not os.path.exists(confdir) ):
				os.makedirs(confdir)

			self.modspkl = os.path.join(confdir, self.modspkl)
			self.confpkl = os.path.join(confdir, self.confpkl)
			self.filepkl = os.path.join(confdir, self.filepkl)
		else:
			self.defaults['wowdir'] = ""

		self.loadConfig()
		self.startmutex.unlock()

		return True

	def __del__(self):
		self.saveConfig()
	
	def log(self, str):
		'''
		Logs str to the self.loglines variable for later user
		'''
		self.loglines.append(str)

	def out2(self, str):
		'''
		Minor output message
		'''
		self.log("**" + str)

	def error(self, str):
		'''
		Minor output message
		'''
		self.log("**" + str)
		self.errors.append(str)
		

	def out(self, str, nolog = 0):
		'''
		Output message logged by default, notlogged if nolog=1
		'''
		if nolog == 0:
			self.log("*" + str)
		
	def gauge(self, i, max):
		'''
		This is a skeleton function used in UIs
		'''
		pass

	def getoption(self, name, default = True):
		'''
		Returns an option specified in name
		'''
		if not self.config.has_key( name ):
			if not self.defaults.has_key( name ) or not default:
				return None
			else:
				#print self.defaults[name]
				return self.defaults[name]

		else:
			#print self.config[name]
			return self.config[name]

	def setoption(self, name, value):
		'''
		Sets an option specified in name to value
		'''
		self.config[name] = value
		
	def loadConfig(self):
		'''
		Loads configuration form the config file
		'''
		if not self.progmutex.testandset():
			return False

		self.mods = [] 
		self.config = {}
		self.files = {} 

		if os.path.exists(self.modspkl) and os.path.getsize(self.modspkl) > 0 :
			self.mods = pickle.load(open(self.modspkl))
			for m in self.mods:
				m.setUpdater(self)
		if os.path.exists(self.confpkl) and os.path.getsize(self.confpkl) > 0 :
			self.config = pickle.load(open(self.confpkl))
		if os.path.exists(self.filepkl) and os.path.getsize(self.filepkl) > 0 :
			self.files = pickle.load(open(self.filepkl))
		self.updateConfig()
		self.progmutex.unlock()

	def saveConfig(self): 
		'''
		Saves current state to the config files
		'''
		#print "saveConfig()"
		modspkl = open(self.modspkl, 'wb')
		confpkl = open(self.confpkl, 'wb')
		filepkl = open(self.filepkl, 'wb')

 		pickle.dump(self.mods, modspkl)
 		pickle.dump(self.config, confpkl)
 		pickle.dump(self.files, filepkl)

		modspkl.close()
		confpkl.close()
		filepkl.close()
		#self.progmutex.unlock()

	def fullClean(self):
		'''
		Cleans installed files and zip files
		'''
		for m in self.mods:
			m.cleaninst()
			m.cleanzip()

		ifacedir = os.path.join(self.getoption('wowdir'), "Interface");

		#if os.path.exists(ifacedir):
		#	shutil.rmtree(ifacedir, True)
		if os.path.exists(self.getoption('zipdir')):
			shutil.rmtree(self.getoption('zipdir'), True)

		self.saveConfig()

	def getModType(self, name):
		'''
		Retuns the type of a mod specified by name
		'''
		return wowaddon.getModType(name)
		
	def getModTypes(self):
		'''
		Returns all possible mod types
		'''
		return wowaddon.getModTypes()

	def addMod(self, type, args):
		'''
		Used by a plugin to announce itself to the class
		'''
		self.mods.insert( 0, type(self, args) )

	def upMod(self, n):
		'''
		Moves mod n up one in the queue
		'''
		if n > 0:
			tmp = self.mods[n]
			self.mods[n] = self.mods[n - 1] 
 			self.mods[n - 1] = tmp
		#print self.mods

	def downMod(self, n):
		'''
		Moves mod n down one in the queue
		'''
		if (n + 1)  < len(self.mods):
			tmp = self.mods[n]
			self.mods[n] = self.mods[n + 1] 
 			self.mods[n + 1] = tmp
		#print self.mods
		

	def delMod(self, n):
		'''
		Deletes the mod from the queue and cleans the zip files and such up
		'''
		self.mods[n].cleanzip()
		self.mods[n].cleaninst()
		del self.mods[n]
		#print self.mods
	
	def initialize(self):
		'''
		Initialize the program at run time
		'''
		self.errors = []

		ifacedir = os.path.join(self.getoption("wowdir"), "Interface")

		zipdir = self.getoption("zipdir")
		try:
			if(not os.path.isdir(ifacedir) and not os.path.exists(ifacedir)):
				os.makedirs(ifacedir)
			if(not os.path.isdir(zipdir)):
				os.makedirs(zipdir)
		except OSError:
			self.error("Could not make/create Interface dir")
			#raise FileError

	def run(self):
		'''
		This does everything, updates and install mods
		'''
		if not self.progmutex.testandset() or self.startmutex.test():
			return False
			
		self.out2("Starting....")
		#self.setoption("ifacedir", "iface")
		steps = 6
		total = len(self.mods )*steps
		i = 0
		self.initialize()
		for m in self.mods:
			try:
				name = m.getname()
				#name = m.name
			except:
				name = m.name
			self.out2("Checking %s ..." % name)
			try:
				if not m.isuptodate():
					try:
						i+=1; self.gauge(i, total)
						self.out2("Cleaning up zipfile for %s ..." % name)
						m.cleanzip()
						i+=1; self.gauge(i, total)
					except FileError, e:
						self.error("Error cleaning zipfile for %s: %s." % (name, e))
						continue
						
					try:
						self.out2("Updating %s ..." % name)
						m.update()
					 	i+=1; self.gauge(i, total)
					except wowaddon.DownloadError, e:
						self.error("Error on checking version for %s: %s %s." % (name, e.__class__, e) )
						continue

					try:
	
						self.out2("Cleaning up old install files for %s ..." % name)
						m.cleaninst()
						i+=1; self.gauge(i, total)
					except wowaddon.FileError, e:
						self.error("Error cleaning old install files for %s: %s." % (name, e))
						continue
	
					try:
						self.out2("Unzipping %s ..." % name)
						m.unzip()
						i+=1; self.gauge(i, total)
					except wowaddon.FileError, e:
						self.error("Error unzipping %s: %s." % (name, e))
						continue

					try:
						self.out2("Copying %s ..." % name)
						m.copy()
						self.saveConfig()
						i+=1; self.gauge(i, total)
					except wowaddon.FileError, e:
						self.error("Error copying %s: %s." % (name, e))
						continue
				else:
					self.out2("%s is up to date." % name)
					i+=steps; self.gauge(i, total)
			except (ParseError, DownloadError), e:
				self.error("Error on checking version for %s: %s %s." % (name, e.__class__, e) )
				continue


		self.out2("Done.")
		self.out("Done.")
		self.progmutex.unlock()
		return 

	def abort(self):
		'''
		Not used at the moment
		'''
		# Method for use by main thread to signal an abort
		self._want_abort = 1

	def updateConfig(self):
		'''
		Function called at runtime to initialize saved values
		'''
		if self.config == {}:
			pver = self.getoption('version')
		else:
			pver = self.getoption('version', False)
			if pver == None:
				pver = 1

		if pver == 1:
			pver += 1
		if pver == 2:
			self.mods = []
			pver += 1

		self.setoption("version", pver)	
		self.saveConfig()	

#	def registerFile(self, file, mod):
#		if not files.has_key(file):
#			files[file] = 1
#	def unregisterFile(self, file, mod):
#		if not files.has_key(file):
#			files[file] = 0
		
if __name__ == "__main__":
	pass

