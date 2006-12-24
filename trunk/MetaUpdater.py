#!/usr/bin/python
'''
This part of the prgram updates any program files that need updating and then
runs the actual program.
'''
__author__    = "Patrick Butler <pbutler@killertux.org>"
__version__   = "$Revision: 31 $"
__copyright__ = "Copyright 2005,2006 Patrick Butler"
__license__   = "GPL Version 2"

import wx
import shutil
import os.path
import os
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
xmlurl = "http://wowaddonupdater.sf.net/updates/updates-v3.xml"
xmllocal = "manifest.xml"


class MetaUpdaterFrame(wx.Frame):
	def __init__(self, parent, id, title, text ):
		wx.Frame.__init__(self, parent, id, title, wx.DefaultPosition, wx.Size(500, 400))
		self.count = 0 
		okbtn = wx.Button(self, wx.ID_OK)

		#self.Bind(wx.EVT_CLOSE, self.OnExit) 
		okbtn.Bind(wx.EVT_BUTTON, self.OnExit) 
		self.text = wx.TextCtrl(self, style=wx.TE_MULTILINE)
		mainbox = wx.BoxSizer(wx.VERTICAL)
		mainbox.Add(self.text, 1, wx.ALL|wx.EXPAND|wx.GROW, border=5)
		mainbox.Add(okbtn, 0, wx.ALL|wx.ALIGN_RIGHT, border=20)

		self.text.SetValue(text) 
		self.text.SetEditable(False) 
		self.SetAutoLayout(True) 
		self.SetSizer(mainbox)

	def OnExit(self, e):
		self.Close()

class MetaUpdaterApp(wx.App):
	def __init__(self, text):
		self.text = text
		wx.App.__init__(self, 0)

	def OnInit(self):
		self.frame = MetaUpdaterFrame(None, -1, 'Updates found', self.text)
		self.frame.Show(True)
		return True


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
		
def checkUpdates():
	frame = None 
	theZip = winZip
	socket.setdefaulttimeout(5)
	updatedFileset = []
	updating = False
	try: 
		xml = urllib.urlopen(xmlurl).read()
		if not xml[:7] == "<files>":
			raise IOError, "Inavalid file"
		files = UpdateXML.parseString(xml)
		if not os.path.isdir(updatesDir): 
			os.makedirs(updatesDir)
		if not os.path.isdir( os.path.join(updatesDir, ".tmp") ): 
			os.makedirs( os.path.join(updatesDir, ".tmp") )

		i = 0
		for f in files.keys():
			i += 1
			xmlhash = files[f]['md5']
			tmpfile = os.path.join(updatesDir, ".tmp", f) 
			updatesFile = os.path.join(updatesDir, f) 
			curmd5 = md5FromFile( updatesFile ) 
			if curmd5 == None:
				curmd5 = md5FromZip(f, theZip)
			if xmlhash != curmd5:
				if not updating:
					updating = True
				#print "Downloading update for", f
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
		#print "Update error", e
		pass
	shutil.rmtree( os.path.join( updatesDir, ".tmp"), True)

	return updating

if __name__ == "__main__":
	if not os.path.exists(updatesDir):
		os.mkdir(updatesDir)
	sys.path.insert(0, updatesDir)
	changelog = os.path.join(updatesDir, 'changelog')
	if checkUpdates():
		text = "No changelog available\n"
		if os.path.exists(changelog):
			f = open(changelog)
			text = f.read()
			f.close()
		app = MetaUpdaterApp(text)
		text = None
		app.MainLoop()
	import updater_gui
        app = updater_gui.UpdaterApp(0)
	app.MainLoop()
		
