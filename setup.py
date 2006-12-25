#!/usr/bin/python
'''
Build file
'''

__author__    = "Patrick Butler <pbutler@killertux.org>"
__version__   = "$Revision: 31 $"
__copyright__ = "Copyright 2005,2006 Patrick Butler"
__license__   = "GPL Version 2"

import sys
from distutils.core import setup
import platform
if platform.system() == "Darwin":
	import py2app
	import shutil
	sys.argv.append("py2app")
	opts =  { 'site_packages': True,
                'optimize' : 2,
        #        'compressed' : 1,
		'iconfile' : 'updater_gui.icns', 
		}

	tgt = { 'script' : "MetaUpdater.py", #updater_gui.py",
		'name' : 'WoW AddOn Updater', 
		#'icon_resources' : [ ( 0, "updater_gui.icns") ] ,
		'dest_base' : "WoW AddOn Updater", }
	setup(
		app = [ tgt ], 
		#'updater_gui.py'],
		
                options={"py2app": dict(opts)}
	)
	shutil.copy("updater_gui.icns", "dist/WoW AddOn Updater.app/Icon\015")

elif platform.system() == "Windows":
	sys.argv.append("py2exe")
	sys.argv.append("-b")
	sys.argv.append("2")


	import py2exe
	
	tgt = { 'script' : "MetaUpdater.py",
		'dest_base' : "updater",
		'icon_resources' : [ ( 0, "updater.ico") ] }

	setup(name="WoW AddOn Updater",
		windows=[ tgt ],
		#excludes = ["pywin", "pywin.debugger", "pywin.debugger.dbgcon",
		#    "pywin.dialogs", "pywin.dialogs.list",
		#    "Tkconstants","Tkinter","tcl" ],
		data_files=[(".", 
		            ["unzip.exe", "unrar.exe", "updater.ico"])],
	)
