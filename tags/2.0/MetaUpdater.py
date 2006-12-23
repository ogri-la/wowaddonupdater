#!/usr/bin/python
'''
This part of the prgram updates any program files that need updating and then
runs the actual program.
'''
__author__    = "Patrick Butler <pbutler@killertux.org>"
__version__   = "$Revision: 31 $"
__copyright__ = "Copyright 2005,2006 Patrick Butler"
__license__   = "GPL Version 2"

import shutil
import os.path
import sys
import urllib
import socket
from zipfile import ZipFile;
import md5
import UpdateXML
#import updater_gui

macZip = ""
winZip = "library.zip"
updatesDir = "updates"
xmlurl = "http://wowaddonupdater.sf.net/updates/updates.xml"

def md5FromFile(file):
	if not os.path.exists(file):
		return None
	try:
		bytes = open(file,"r").read()
		return md5.new(bytes).hexdigest()
	except:
		return None

def md5FromZip(zip, file):
	if not os.path.exists( zip ):
		return None
	try:
		zf = ZipFile(zip, "r")
		if file in zf.namelist():
			bytes = zf.read(file)
			return md5.new(bytes).hexdigest()
		else:
			return None
	except:
		return None

if __name__ == "__main__":
	theZip = winZip
	sys.path.insert(0, updatesDir)
	socket.setdefaulttimeout(5)
	updatedFileset = []
	try: 
		xml = urllib.urlopen(xmlurl).read()
		if not xml[:7] == "<files>":
			raise IOError, "Inavalid file"
		files = UpdateXML.parseString(xml)
		if not os.path.isdir(updatesDir): 
			os.makedirs(updatesDir)
		if not os.path.isdir( os.path.join(updatesDir, ".tmp") ): 
			os.makedirs( os.path.join(updatesDir, ".tmp") )
		safe = True 
		for f in files.keys():
			xmlhash = files[f]['md5']
			tmpfile = os.path.join(updatesDir, ".tmp", f) 
			updatesFile = os.path.join(updatesDir, f) 
			curmd5 = md5FromFile( updatesFile ) 
			if curmd5 == None:
				curmd5 = md5FromZip(f, theZip)
			if xmlhash != curmd5:
				print "Downloading update for", f
				url = files[f]['source']
				urllib.urlretrieve(url, tmpfile)
				tmpmd5 = md5FromFile( tmpfile )
				#print tmpfile, tmpmd5,  files[f]['md5']
				if tmpmd5 != xmlhash:
					raise IOError, "Bad download %s!=%s" % ( xmlhash, tmpmd5)
				updatedFileset.append( (tmpfile, updatesFile) )

		for tup in updatedFileset:
			(t, u) = tup
			if os.path.exists( u ):
				os.unlink( u )
			shutil.move(t, u)
	except IOError, e:
		print "Update error", e
	shutil.rmtree( os.path.join( updatesDir, ".tmp"), True)
				
	import updater_gui
        app = updater_gui.UpdaterApp(0)
	app.MainLoop()
		
