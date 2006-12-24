#!/usr/bin/pythonw
'''
This defines common functions and the interface for the plugin API

the following methods are required
getname
getnewver
getcurver
isuptodate
cleanzip
update
cleaninst
unzip
copy
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
import zipfile
from zipfile import ZipFile, ZIP_DEFLATED
import md5
import time

import socket
import urllib2

#Mods may throw these 
class CopyError(Exception): pass
class DownloadError(Exception): pass
class ParseError(Exception): pass
class FileError(Exception): pass



modtypes = dict()

def addModType(name, mod):
	modtypes[name] = mod

def getModTypes():
	return modtypes.keys()[:]

def getModType(name):
	if not modtypes.has_key(name):
		return None
	else:
		return modtypes[name]

def cleanuphtml(text):
	def asciicode(match):
		return chr(int(match.group(1)))

	text = text.replace("&160;", " ")
	text = text.replace("&nbsp;", " ")
	text = re.sub("&#(\d{1,3});", asciicode, text)
	text = text.replace("&lt;", "<")
	text = text.replace("&gt;", ">")
	text = text.replace("&gt;", ">")
	return text


class Plugin:
	def __init__(self, updater , args):
		self.updater = updater
		self.type = "Default"
		self.pluginversion = 0
		self.zipfile = ""

		self.infiles = []
		self.outfiles = []

		self.tmpdir = ""
		self.curversion = None
		self.newversion = None

		self.name = ""
		self.link = ""

		self.lastcheckTS = 0

		self.step = 0
		return

	def getnewver(self):
		self.getinfo() 
		return self.newversion
	
	def timemutex(self, int):
		if time.time() - self.lastcheckTS >= 60:
			self.lastcheckTS = time.time()
			return  False
		return True

	def getcurver(self):
		return self.curversion 
	
	def getname(self):
		if self.name == "":
			self.getinfo()
		return self.name

	def getinfo(self):
		pass

	def isuptodate(self):
		newver = self.getnewver() 
		if self.getcurver() == None:
			self.out("NONE")
			return False 
		wowdir = self.getoption("wowdir")
		for f in self.outfiles:
			if not os.path.exists(os.path.join(wowdir, f)):
				self.out(f + " does not exist reinstalling")
				return False
		if newver != self.getcurver() :
			self.out( str(newver) + " != " + str(self.getcurver()) )
		return newver == self.getcurver() #and os.path.exists(self.zipfile)

	def cleanzip(self):
		try:
			if os.path.exists(self.zipfile):
				os.unlink(self.zipfile)
			self.zipfile = ""
			self.infiles = []
		except OSError, e:
			raise CleanError, e

	def cleaninst(self):
		
		def cmpdir(a,b):
			if(a.count(os.sep) < b.count(os.sep)):
				return 1
			if(a.count(os.sep) > b.count(os.sep)):
				return -1
			return 0;
		
		#I want to delete files specifically not wildcard them
		#this makes it easier
		self.outfiles.sort(cmpdir)

		try:
			if os.path.isdir(self.tmpdir):
				shutil.rmtree(self.tmpdir, True)
			self.tmpdir = ""
			self.step = 0
			wowdir = self.getoption('wowdir')
			ifacedir = os.path.join(wowdir, "Interface")

			#paranoid check
			for f in self.outfiles[:]:
				if  f == '':
					self.outfiles.remove(f);

			#files
			for f in self.outfiles[:]:
				file = os.path.join(wowdir, f)
				if os.path.exists(file) and not os.path.isdir(file):
					os.unlink(file)
					self.outfiles.remove(f)

				d = os.path.dirname(f)
				if d == '':
					continue
				dir = os.path.join(wowdir, d)
				if os.path.exists(dir) and os.path.isdir(dir):
					try:
						os.rmdir(dir)
					except os.error:
						self.log("Didn't delete dir:"+dir)

			#directories
			for f in self.outfiles[:]:
				dir = os.path.join(wowdir, f);
				print dir
				if (os.path.exists(dir) and os.path.isdir(dir)):
					os.rmdir(dir);
				if not os.path.exists(dir):
					self.outfiles.remove(f);

			#print self.outfiles;
		except OSError, e:
			#raise CleanError, e
			pass

	def update(self):
		zipdir = self.getoption('zipdir')

		def dhook(blocks, bsize, totsize):
			self.out("Downloading... %dk" % (blocks*bsize/1024), 1)

		if self.link == "":
			self.getinfo();
		#print self.link;
		name = self.id+".zip"
		self.out("%s (%s)" % (self.link, name))
		zipfile = os.path.join(zipdir, self.zipfilename)

		link = self.link
		link = link.replace(" ", "%20")

		try:
			urllib.urlretrieve(link, zipfile, dhook)
		except IOError, e:
			raise DownloadError, e;
		self.zipfile = zipfile
		self.out("Downloading... done")
		return

	def unzip(self):
		if(self.zipfile == "" ):
			raise "No zip d/led"
		self.tmpdir = self.zipfile[0:len(self.zipfile)-4]
		self.infiles = unzip(self.zipfile, self.tmpdir)
		return

	def copy(self):
		wowdir = self.getoption("wowdir")
		ifacedir = os.path.join(wowdir, "Interface")

		if( not os.path.exists(ifacedir) ):
			os.makedirs(ifacedir)
		tmpdir = self.tmpdir

		self.outfiles = []
		def checkstart(files, str):
			str = str.lower()
			for f in files:
				if(f.lower().startswith(str + os.sep) ):
					return True
			return False

		try:
			if(checkstart(self.infiles, "Interface") ):
				#move_ow(os.path.join(tmpdir,"Interface"), ifacedir)
				names = os.listdir(tmpdir)
				for n in names:
					move_ow( os.path.join(tmpdir, n), 
						 os.path.join(wowdir, n))

				self.outfiles[:] = self.infiles
				#for f in self.infiles:
				#	self.outfiles.append(f)
					#if f.lower().startswith("interface"):
					#	self.outfiles.append(f[10:])
					#else:
					#	self.outfiles.append( os.path.join("..", f) )
			elif(checkstart(self.infiles, "AddOns") ):
				names = os.listdir(tmpdir)
				for n in names:
					move_ow( os.path.join(tmpdir, n), 
						 os.path.join(ifacedir, n))
				#move_ow(os.path.join(tmpdir, "AddOns"), 
				#	os.path.join(ifacedir, "AddOns") )
				#if(checkstart(self.infiles, "FrameXML") ):
				#	move_ow(os.path.join(tmpdir, "FrameXML"), 
				#		os.path.join(ifacedir, "FrameXML") )
				for f in self.infiles:
					self.outfiles.append(os.path.join("Interface",  f))
			else:
				names = os.listdir(tmpdir)
				for n in names:
					move_ow(os.path.join(tmpdir, n),
						os.path.join(ifacedir, "AddOns", n) )
				for f in self.infiles:
					self.outfiles.append(os.path.join("Interface", "AddOns", f))


			#create copy so removes doesnt break
			#print self.outfiles[1:10] 
			for f in self.outfiles[:] :
				realfile = os.path.join(wowdir, f);
				if ( (not os.path.exists(realfile)) or 
				     f == '' or
				     f.strip(os.sep).lower() == '' or 
				     f.strip(os.sep).lower() == 'addons' or 
				     f.strip(os.sep).lower() == 'framexml' or
				     f.strip(os.sep).lower() == os.sep ):
					self.outfiles.remove(f)
					if (not os.path.exists(realfile) ):
						print "**************ERROR ", f, "NOT FOUND*********"
			
			#print self.outfiles
			self.postcopy()
		except OSError, e:
			raise CopyError, e
		self.curversion = self.newversion
		return

	def cleantmpdir(self):
		if(self.tmpdir != "" and self.tmpdir != "/"):
			shutil.rmtree(self.tmpdir, True)
		self.tmpdir = ""
		return

	#def cleaninstall(self):
	#	ifacedir = self.getoption("ifacedir")
	#	for f in self.outfiles:
	#		fp = ifacedir 
	#		#os.path.join(ifacedir, f[10:])
	#		if(not os.path.isdir(fp) and os.path.exists(fp)):
	#			os.unlink(fp)
	#			self.outfiles.remove(f)
	#	for f in outfiles:
	#		fp = ifacedir #os.path.join(ifacedir, f[10:])
	#		if os.path.exists(fp):
	#			os.removedirs(fp)
	#	return

	def cleanzip(self):
		if( self.zipfile == "" and os.path.exists(self.zipfile) ):
			os.unlink(self.zipfile)
		self.zipfile = ""
	 	return
	
	def postcopy(self):
		try:
			shutil.rmtree(self.tmpdir, True)
		except os.error:
			self.log("Not all files are deleted in the tmpdir: "+ self.tmpdir)
		return

	def getoption(self, name):
		return self.updater.getoption(name)

	def setoption(self, name, value):
		return self.updater.setoption(name, value)
		
	def log(self, str):
		if self.updater != None:
			self.updater.log(str)
		else:	
			print "LOG:", str

	def out(self, str, nolog = 0):
		if self.updater != None:
			self.updater.out(str, nolog)
		else:	
			print "LOG:", str

	def out2(self, str):
		if self.updater != None:
			self.updater.out2(str)
		else:	
			print "LOG:", str

	def __getstate__(self):
		odict = self.__dict__.copy() # copy the dict since we change it
		if odict.has_key('updater'):
			del odict['updater']   
		return odict

	def setUpdater(self, updater):
		self.updater = updater

	def getURL(url, data=None):
		timeout = 10
		# timeout in seconds
		socket.setdefaulttimeout(timeout)

		req = urllib2.Request(url, data)
		return urllib2.urlopen(req)


	def help():
		return "Tell the stupid author he needs to write documentation"
	help = staticmethod(help)


def copytree(src, dst, symlinks=0):
	if( not os.path.isdir(src) ):
		shutil.copy2(src, os.path.join(dst, os.path.basename(src) ))
		return
	names = os.listdir(src)
	if(not os.path.exists(dst) ):
		os.mkdir(dst)
	for name in names:
		srcname = os.path.join(src, name)
		dstname = os.path.join(dst, name)
		try:
			if symlinks and os.path.islink(srcname):
				linkto = os.readlink(srcname)
				os.symlink(linkto, dstname)
			elif os.path.isdir(srcname):
				copytree(srcname, dstname, symlinks)
			else:
				shutil.copy2(srcname, dstname)
		except (IOError, os.error), why:
			print "Can't copy %s to %s: %s" % (`srcname`, `dstname`, str(why))

def unzip( path, outpath ):
	files = []
	if not os.path.exists(outpath):
			os.makedirs(outpath)
		
	if isRarFile(path):
		output = os.popen("unrar vb " + path).read()
		if(output[0] == "[") :
			#print "Sorry no dice with " + path
			raise UnzipError

		lines = re.split(r"[\r\n]+", output)
		for l in lines:
			if  l != '':
				files.append(l)

		os.popen("unrar x " + path + " "+ outpath)
		for i in range(len(files)):
			files[i] = files[i].replace('/', os.sep).lstrip(os.sep)
		return files
	
			
	#Only continue this if it could possibly be a zipfile
	if not isZipFile(path):
		return []

	#if it's not going to work with the inhome libs use the exev
	if(not zipfile.is_zipfile(path) ):
		output = os.popen("unzip -qq -l " + path).read()
		if(output[0] == "[") :
			#print "Sorry no dice with " + path
			raise UnzipError

		lines = re.split(r"[\r\n]+", output)
		for l in lines:
			lst = re.split(r"\s+", l.strip(), 3)
			if (len(lst) > 3):
				files.append(lst[3])
		os.popen("unzip -qq -d " + outpath + " "+ path)
		for i in range(len(files)):
			files[i] = files[i].replace('/', os.sep).lstrip(os.sep)
		return files

	archive = ZipFile(path, "r")
	for info in archive.infolist():
		name = info.filename
		filesize = info.file_size

		outname = name
		if(platform.system() == "Windows"):
			outname = name.replace('/', os.sep)

		outname = os.path.join(outpath, outname.lstrip(os.sep))
		
		isdir = ((info.external_attr & 0xff) & 0x10)
		
		if name[-1] == '/' or isdir != 0:
			if not os.path.exists(outname):
				os.makedirs(outname)
			continue
			tmp = name.replace('/', os.sep).lstrip(os.sep)
			if tmp[-1] != os.sep:
				tmp = tmp + os.sep
			files.append(tmp)
		else:
			files.append(name.replace('/', os.sep).lstrip(os.sep))


		if not os.path.exists( os.path.dirname(outname)):
			os.makedirs(os.path.dirname(outname))

		# Write files to disk
		temp = open(outname, "wb");  # create the file
		data = archive.read(name);   # read the binary data
		temp.write(data)
		temp.close()
		
	archive.close()
	return files

def hashfile(file):
	f = open(file, "rb")
	hash = md5.new( f.read() )
	f.close()
	return hash.hexdigest()

def move_ow(src, dst):
	#print src, "\t", dst
	if ( not os.path.exists(dst) ): #if not there
		if ( not os.path.exists(os.path.dirname(dst)) ): #if not there
			os.makedirs(os.path.dirname(dst))
		#if os.path.isdir(src):
		#	print "\tmakedir", dst
		#	os.makedirs(dst)
		#print "\tmovedir", dst
		shutil.move(src, dst)
		return
	if ( not os.path.isdir(src) ): #if file
		os.unlink(dst)
		shutil.move(src, dst)
		return
	names = os.listdir(src) 
	for name in names: 
		srcname = os.path.join(src, name) 
		dstname = os.path.join(dst, name) 
		try: 
			if os.path.isdir(srcname): 
				move_ow(srcname, dstname)
			else: 
				shutil.move(srcname, dstname) 
		except (IOError, os.error), why: 
			print "Can't move %s to %s: %s" % (`srcname`, `dstname`, str(why))
	

def nopatch(ifacedir, outfiles):
	for f in outfiles:
		dir = os.path.join(ifacedir, f)
		#print dir
		if ( os.path.isdir(dir) ):
			file = os.path.join(dir, "nopatch")
			open(file, "w")
			#print file, f
			outfiles.append(os.path.join(f, "nopatch"))

def isZipFile(file):
	f = open(file)
	magic = f.read(4)
	f.close()
	return magic == "PK\003\004"

def isRarFile(file):
	f = open(file)
	magic = f.read(5)
	f.close()
	return magic == "Rar!\x1a"

