#!/usr/bin/python
'''
The Cosmos plugin, at the moment it only updates Cosmos to the latest version.
'''
__author__    = "Patrick Butler <pbutler@killertux.org>"
__version__   = "$Revision: 31 $"
__copyright__ = "Copyright 2005,2006 Patrick Butler"
__license__   = "GPL Version 2"

import wowaddon
import re
import os
import urllib
import socket
import struct
from time import time
import zlib

class Plugin(wowaddon.Plugin):
	def __init__(self, updater, args):
		wowaddon.Plugin.__init__(self, updater, args)
		self.id = ""
		self.name = "Cosmos"
		self.type = "cosmos"
		self.distro = 4
		self.socket = None
		zipdir = self.getoption('zipdir')
		self.tmpdir = os.path.join(zipdir, "cosmos-"+str(int(time())))
		self.curfl = {}
		self.newfl = {}

	def connect(self):
		if self.socket != None:
			return		
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
		self.setdistro = False
		self.socket.connect(("patch.cosmosui.org", 8087))

	def disconnect(self):
		self.socket.close()
		self.socket = None
		self.setdistro = False
	

	def send(self, message):
		messlen = self.socket.send(message)
		if messlen != len(message): 
			self.error("Failed to send complete message, socket broken")

	def recv(self, n):
		data = self.socket.recv(n)
		return data

	def getname(self):
		return self.name

	def isuptodate(self):	
		return False

	def getnewver(self):
		#prevent reconnecting too many times 5 minutes sounds good
		if time() - self.lastcheckTS < 300:
			return self.newversion
 		self.lastcheckTS = time()
		self.connect()
		self.getReleases()
		fl = self.getFileList(self.distro)
		self.send("c\nCosmos.txt\nC\n")
		#cosmos.txt shouldn't be too long... we hope
		data = self.recv(fl["Cosmost.txt"]['csize'])
		data = zlib.decompress(data)
		match = re.search("^r(\d+)", s, re.M)
		if match == None:
			raise wowaddon.ParseError("Couldn't find version")
		self.newversion = match.group(1)
		self.disconnect()
		return self.newversion 
	
	def cleaninst(self):
		pass

	def update(self):
		wowdir = self.updater.getoption("wowdir")
		self.connect()
		rel = self.getReleases()
		self.out("release: %s" % rel[self.distro])
		self.newfl = self.getFileList(self.distro)
		newfiles = []
		for f in self.newfl.keys():
			if self.curfl.has_key(f):
				if not os.path.exists(os.path.join(wowdir, f)):
					newfiles.append(f)
				if self.curfl[f]['hash'] != self.newfl[f]['hash']:
					newfiles.append(f)
			else:
				newfiles.append(f)
		self.getFiles(newfiles, self.newfl)
	
	def copy(self):
		wowdir = self.updater.getoption("wowdir")
		for f in self.curfl.keys():
			if not self.curfl.has_key(f):
				os.unlink( os.path.join(wowdir, f) )
		wowaddon.Plugin.copy(self)
		self.curfl = self.newfl
		self.newfl = []
		self.outfiles = [] 
		for f in self.curfl.keys():
			self.outfiles.append( os.path.join(wowdir, f) )

	def cleanzip(self):
		pass

	def unzip(self):
		if not os.path.exists( self.tmpdir ):
			os.makedirs( self.tmpdir )
		self.disconnect()

	def getReleases(self):
		self.connect()
		self.send("D\n")
		data = self.recv(4096)
		rels = {}
		for line in data.split("\n"):
			if line == 'D':
				break
			(num, name) = line.split(" ", 1)
			rels[int(num)] = name
		return rels

	def getFileList(self, rel):
		self.connect()
		#if self.setdistro == True:
		#	return
		self.send( "P %d\n" % rel)
		self.setdistro = True

		data = self.recv(4096)
		while  data.find("\nD\n") == -1 and data != "D\n":
			data += self.recv(4096)
		lines = data.split("\n")
		files = {}
		for i in range(0, len(lines), 3):
			if lines[i] == "D":
				break
			name = lines[i]
			name = name.replace("\\", os.sep)
			(fsize, csize) = lines[i + 1].split(" ", 2)
			hash = lines[i + 2]
			files[name] = {	'hash' : hash, 
					'fsize' : int(fsize), 
					'csize' : int(csize) }
		return files
	
	
	def getFiles(self, files, flist):
		self.connect()
		wowdir = self.getoption("wowdir")
		if files == []:
			self.out("Cosmos: Nothing to update")
			return
		#Solve a problem that shouldn't exist
		if self.setdistro == False:
			self.getRelease(self.distro)
		tot = len(files)
		i = 1
		msg = ""
		for file in files:
			file = file.replace(os.sep, "\\")
			#self.out("requesting %s %d/%d " % ( file, i,tot) )
			msg += "c\n" +file +"\n" 
			i += 1
		self.send(msg+"C\n")

		for file in files:
			self.out("Cosmos: getting file: " +file) 
			infile = os.path.join(self.tmpdir, file);
			dir = os.path.dirname(infile)
			if not os.path.exists( dir ):
				os.makedirs( dir )
			fp = open(infile, "wb")
	
			csize = flist[file]['csize'] 
			getsize =  4096
			gotten  = 0
			decomp = zlib.decompressobj()
			while gotten < csize:
				if csize - gotten < getsize:
					getsize =  csize - gotten
				cdata = self.recv(getsize)
				gotten += len(cdata)
				data = decomp.decompress(cdata)
				fp.write(data)
			fp.close()
			self.infiles.append(file)
			#if len(data) != flist[file]['fsize']:
			#	self.error("Error: only got", len(data),"bytes")
			self.out("Cosmos: done getting files.")

	def __getstate__(self): 
		odict = wowaddon.Plugin.__getstate__(self)
		odict['socket'] = None  
		return odict


	def help():
		return """
Nothing much to say here... Just add it and it should work
"""
	def argdesc():
		return None
	help = staticmethod(help)
	argdesc = staticmethod(argdesc)
	

wowaddon.addModType("Cosmos", Plugin)

