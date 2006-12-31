#!/usr/bin/pythonw
'''
This is the GUI front end for the updater
'''

__author__    = "Patrick Butler <pbutler@killertux.org>"
__version__   = "$Revision: 31 $"
__copyright__ = "Copyright 2005,2006 Patrick Butler"
__license__   = "GPL Version 2"


import sys 
import platform
import threading
import wx
import wx.gizmos
import UpdaterWizard
import updater

EVT_RESULT_ID = wx.NewId()

def EVT_RESULT(win, func):
	win.Connect(-1, -1, EVT_RESULT_ID, func)

class ResultEvent(wx.PyEvent):
	"""Simple event to carry arbitrary result data"""
	def __init__(self, data):
		wx.PyEvent.__init__(self)
		self.SetEventType(EVT_RESULT_ID)
		self.data = data

class UpdaterApp(wx.App, updater.Updater):
	def OnInit(self):
		updater.Updater.__init__(self)
		self.main = UpdaterFrame(self, None, -1, "WoW AddOn Updater")
		self.main.Show(True)
		return True

	def error(self, str):
		updater.Updater.error(self, str)
		wx.PostEvent(self.main,ResultEvent([4, str]))

	def out2(self, str):
		updater.Updater.out2(self, str)
		wx.PostEvent(self.main,ResultEvent([2, str]))

	def out(self, str, nolog = 0): 
		updater.Updater.out(self, str, nolog)
		wx.PostEvent(self.main,ResultEvent([1, str]))

	def gauge(self, i, max):
		updater.Updater.gauge(self, i, max)
		wx.PostEvent(self.main,ResultEvent([3, i*100/max]))


class UpdaterFrame(wx.Frame):
	def __init__(self, app, parent, ID, title):
		wx.Frame.__init__(self, parent, ID, title, size=(600,-1))
		panel = wx.Panel(self, -1)
		self.app = app
		self.count = 0
		self.icon = None
		# XXX see about integrating this into our app or a resource file
		try:            # - don't sweat it if it doesn't load
			if platform.system() != "Darwin":
				self.icon = wx.Icon("updater.ico", wx.BITMAP_TYPE_ICO)
				self.SetIcon(self.icon)
		finally: 
			pass


		mainbox = wx.BoxSizer(wx.VERTICAL)
		btnbox = wx.BoxSizer(wx.HORIZONTAL)
		textbox = wx.BoxSizer(wx.HORIZONTAL)


		#menubar stuff
		menubar = wx.MenuBar()
		filemenu = wx.Menu()
		helpmenu = wx.Menu()

		logitm = filemenu.Append(-1,'L&og','Review the Log')
		exititm = filemenu.Append(-1,'E&xit','Terminate the program') 
		aboutitm = helpmenu.Append(wx.ID_ABOUT, '&About', 'About this program')
		helpitm = helpmenu.Append(-1,'Set the Preferences', '')

		self.Bind(wx.EVT_MENU, self.OnLog, logitm)
		self.Bind(wx.EVT_MENU, self.OnAbout, aboutitm)
		self.Bind(wx.EVT_MENU, self.OnExit, exititm)
		if "__WXMAC__" in wx.PlatformInfo:
			wx.App.SetMacExitMenuItemId(exititm.GetId())
		menubar.Append(filemenu,'&File')
 		menubar.Append(helpmenu,'&Help')
		self.SetMenuBar(menubar)

		#other stuff
		self.gauge = wx.Gauge(panel, -1, 100, size=(300, 25))
		self.startbtn = wx.Button(panel, wx.ID_OK)
		self.prefbtn = wx.Button(panel, -1, "Preferences") #wx.ID_STOP)
		self.text = wx.StaticText(panel, -1, "Press OK to begin")

		self.Bind(wx.EVT_BUTTON, self.OnOk, self.startbtn)
		self.Bind(wx.EVT_BUTTON, self.OnPref, self.prefbtn)

		btnbox.Add(self.startbtn, 1, wx.RIGHT, 10)
		btnbox.Add(self.prefbtn, 1)
		textbox.Add(self.text, 1)
		mainbox.Add((0, 50), 0)
		mainbox.Add(self.gauge, 0, wx.ALIGN_CENTRE)
		mainbox.Add((0, 30), 0)
		mainbox.Add(btnbox, 1, wx.ALIGN_CENTRE)
		mainbox.Add(textbox, 1, wx.ALIGN_CENTRE)

		panel.SetSizer(mainbox)
		self.statusbar = self.CreateStatusBar()
		self.Centre()

		EVT_RESULT(self, self.OnResult)
		self.prefframe = None 
		self.logframe = None

	def OnResult(self, event):
		if event.data == None:
			pass
		elif event.data[0] == 1:
			self.statusbar.SetStatusText(event.data[1])
		elif event.data[0] == 2:
			self.text.SetLabel(event.data[1])
		elif event.data[0] == 3:
			self.gauge.SetValue(event.data[1])
		elif event.data[0] == 4: 
			wx.MessageDialog(self, event.data[1], "Error", style=wx.ICON_ERROR).ShowModal()

	def OnLog(self, event):
		if self.logframe == None:
 			self.logframe = LogFrame(self.app, self)
		text = ""
		for i in self.app.loglines:	
			text = text + i + "\n"
		self.logframe.setText(text)
		self.logframe.Show(True)
		
	def OnOk(self, event):
		if ( self.app.progmutex.test() or self.app.startmutex.test() ):
			return
		self.app.out2("Starting...")
		self.worker = threading.Thread(target=self.app.run)
		self.worker.start()
		#self.app.saveConfig()

	def OnPref(self, event):
		if not self.app.progmutex.testandset() or self.app.startmutex.test() :
			return
		self.app.out2("Loading Preferences...")
		#if self.prefframe == None:
		#	self.prefframe = PrefFrame(self.app, self)
		dlg = PrefFrame(self.app, self) #, self.icon)
		dlg.ShowModal() 
		dlg.Destroy()
		#self.startbtn.Enable(False)
		#self.prefframe.Show(True)
		self.app.out2("Ready")
		self.app.out("")

	def OnExit(self, event):
		self.Close()

	def OnAbout(self, event): 
		dlg = AboutBox(self, self.icon)
		dlg.ShowModal() 
		dlg.Destroy()


class PrefFrame(wx.Dialog):
	def __init__(self, app, parent, ID = -1, title = "Updater Preferences",  style=wx.DEFAULT_FRAME_STYLE):
		wx.Dialog.__init__(self, parent, -1, title, size=(600, -1) )
		#wx.Frame.__init__(self, parent, ID, title, size=(600,-1))
		panel = wx.Panel(self, -1)
		
		#self.Show(True)
		#panel.Show(True)
		self.app = app
		self.count = 0
			
		self.Bind(wx.EVT_CLOSE, self.OnExit)

		#first background controls like staticboxes
		mainbox = wx.BoxSizer(wx.VERTICAL)

		naddmodbox = wx.StaticBoxSizer(
			wx.StaticBox(panel, -1, "Add Mod"), wx.VERTICAL)
		noptionbox = wx.StaticBoxSizer(
			wx.StaticBox(panel, -1, "General Options"), wx.VERTICAL)
		ncurmodbox = wx.StaticBoxSizer(
			wx.StaticBox(panel, -1, "Current Mods"), wx.VERTICAL)
		
		#create controls 
 		self.wowdirctrl = wx.TextCtrl(panel)
 		self.wowdirbtn = wx.Button(panel, -1, "Browse")
 		self.wowdirdia = wx.DirDialog(panel, "WoW Directory")
 		#self.newmoddia = wx.FileDialog(panel, "WoW Directory")

 		self.newmodtype = wx.Choice(panel, choices=self.app.getModTypes())
 		#self.newmodbrs = wx.Button(panel, -1, "Browse")
 		#self.newmodarg = wx.TextCtrl(panel)
 		self.newmodbtn = wx.Button(panel, -1, "Add Mod")

 		self.modlbox = wx.gizmos.EditableListBox(panel, style=wx.gizmos.EL_ALLOW_DELETE)
 		self.modsctrl = self.modlbox.GetListCtrl()
		self.delbtn = self.modlbox.GetDelButton()
		self.dnbtn  = self.modlbox.GetDownButton()
		self.upbtn  = self.modlbox.GetUpButton()
		
		self.helpbtn = wx.Button(panel, -1, "Help")
		self.okbtn = wx.Button(panel, -1, "OK")

		self.cleanbtn = wx.Button(panel, -1, "Cleanup Files")


		#BIND buttons
		self.upbtn.Bind(wx.EVT_BUTTON, self.OnUp)
		self.dnbtn.Bind(wx.EVT_BUTTON, self.OnDown)
		self.delbtn.Bind(wx.EVT_BUTTON, self.OnDel)
		self.helpbtn.Bind(wx.EVT_BUTTON, self.OnHelp)
		self.okbtn.Bind(wx.EVT_BUTTON, self.OnClose)
		self.cleanbtn.Bind(wx.EVT_BUTTON, self.OnClean)
		self.wowdirbtn.Bind(wx.EVT_BUTTON, self.OnBrowse)
		self.newmodbtn.Bind(wx.EVT_BUTTON, self.OnAdd)
		#self.newmodbrs.Bind(wx.EVT_BUTTON, self.OnBrowseArg)
		

		#option box
		optionbox = wx.FlexGridSizer(cols=2, vgap=8, hgap=8)
		noptionbox.Add(optionbox, 1, wx.GROW)
		noptionbox.Add(self.cleanbtn, 1, wx.ALIGN_CENTER|wx.ALL,5)

		optionbox.AddGrowableCol(1, 1)
		optionbox.SetFlexibleDirection(wx.HORIZONTAL)
		wowdirbox = wx.BoxSizer(wx.HORIZONTAL)
		wowdirbox.Add(self.wowdirctrl, 1, wx.RIGHT|wx.GROW|wx.EXPAND, 10)
		wowdirbox.Add(self.wowdirbtn, 0, wx.ALIGN_RIGHT)
		def addoption(label, ctrl):
			optionbox.Add( wx.StaticText(panel, -1, label), 0)
			optionbox.Add( ctrl, 1, wx.GROW )

		addoption("WoW Directory", wowdirbox)

		#add wow mod
		addmodbox = wx.FlexGridSizer(cols=3, vgap=8, hgap=8)
		addmodbox.Add( wx.StaticText(panel, -1, "Source:") )
		addmodbox.Add( self.newmodtype )
		addmodbox.Add( self.newmodbtn)
		#addmodbox.Add( self.newmodarg, 1, wx.GROW|wx.EXPAND)
		#addmodbox.Add( (0,0) )
		#addmodbox.Add( self.newmodbrs )
		#addmodbox.Add( (0,0) )
		naddmodbox.Add(addmodbox, 1, wx.ALIGN_CENTRE)

		ncurmodbox.Add(self.modlbox, 1, wx.EXPAND)

		#all mod box
		modbox = wx.BoxSizer(wx.VERTICAL) #HORIZONTAL)
		modbox.Add( naddmodbox, 1, wx.ALL | wx.EXPAND, border=5 )
		modbox.Add( (500,1) )
		modbox.Add( ncurmodbox, 3, wx.ALL | wx.EXPAND, border=5 )

		#buttons box
		btnbox = wx.BoxSizer(wx.HORIZONTAL)
		btnbox.Add(self.helpbtn, 1, wx.ALIGN_RIGHT|wx.RIGHT, 10)
		btnbox.Add(self.okbtn, 1, wx.ALIGN_RIGHT)
		#btnbox.Add((13,0) )
		
		#mainbox
		mainbox.Add(noptionbox, 0, wx.ALL|wx.EXPAND, border=5)
		mainbox.Add(modbox, 1, wx.ALL | wx.EXPAND, border=5)
		mainbox.Add(btnbox, 0, wx.ALIGN_RIGHT | wx.BOTTOM | wx.RIGHT, border=20)

		panel.SetSizer(mainbox)
		#panel.SetAutoLayout(True)
		#self.SetAutoLayout(True)
		#self.SetSizer(mainbox)
		#panel.Centre()
		panel.Fit()
		self.Fit()
		#self.Centre()
		#mainbox.Layout()

		self.load()

	def load(self):
		for i in range(len(self.app.mods)-1, -1, -1):
			item = wx.ListItem()
			type = self.app.mods[i].type
			id = self.app.mods[i].id
			name = self.app.mods[i].getname()
			item.SetText("%s: %s, %s" %(type, id, name) )
			self.modsctrl.InsertItem(item)

		self.wowdirctrl.SetValue( self.app.getoption('wowdir') )
		return

	def save(self):
 		self.app.setoption('wowdir', self.wowdirctrl.GetValue() )
		self.app.saveConfig()

	def OnUp(self, event):
		n = self.modsctrl.GetNextSelected(-1)
		if( n < 0):
			return 
		self.app.upMod(n)
		event.Skip()

	def OnDown(self, event):
		n = self.modsctrl.GetNextSelected(-1)
		if( n < 0):
			return 
		self.app.downMod(n)
		event.Skip()
	
	def OnDel(self, event):
		n = self.modsctrl.GetNextSelected(-1)
		if( n < 0):
			return 
		self.app.delMod(n)
		self.modsctrl.DeleteItem(n)
		#event.Skip()

	def OnAdd(self, event):
		try:
			label = self.newmodtype.GetStringSelection()
			i = ""
			if label == "":
				return
			type = self.app.getModType(label)
			argdesc = type.argdesc() 
			args = []
			if argdesc != None:
				wizard = UpdaterWizard.UpdaterWizard(argdesc)
				finished = wizard.Run()
				if not finished:
					wizard.Done()
					return
				else:
					args = wizard.getAnswers()
					wizard.Done()
			self.app.addMod(type, args)
			item = wx.ListItem()
			id = self.app.mods[0].id
			name = self.app.mods[0].getname()
			item.SetText("%s: %s, %s" %(type, id, name) )
			self.modsctrl.InsertItem(item)
		except ValueError:
			pass
		except AttributeError,e:
			self.log("Probably nothing but got: %s." %(str(e)))

	def OnBrowse(self, event):
		self.wowdirdia.SetPath(self.wowdirctrl.GetValue() )
		self.wowdirdia.ShowModal()
		self.wowdirctrl.SetValue(self.wowdirdia.GetPath() )

	def OnBrowseArg(self, event):
		#self.newmoddia.SetPath(self.newmodarg.GetValue() )
		#self.newmoddia.ShowModal()
		#self.newmodarg.SetValue(self.newmoddia.GetPath() )
		pass

	def OnHelp(self, event):
		text = """
Wow Dir -- Unless you installed WoW in an odd place this should be correctly set at startup.
"""
		for t in self.app.getModTypes():
			h = self.app.getModType(t).help()
			text += "-------------------------------------\n" + t + ":" + h
		wx.Info(self, text, "Help")

	def OnExit(self, event):
		self.OnClose(event)

	def OnClose(self, event):
		self.Hide()
		self.save()
		#self.Show(False)
		self.app.progmutex.unlock()
		self.app.main.startbtn.Enable(True)

	def OnClean(self, event):
		choice = wxSure(self, "This will delete your Interface directory and delete all AddOns you have installed.  Are you sure you want to do this?")
		if choice == wx.ID_YES:
			self.app.fullclean()

class LogFrame(wx.Frame):
	def __init__(self, app, parent, ID=-1, title="Log"):
		wx.Frame.__init__(self, parent, ID, title, size=(400,600))
		self.app = app
		self.count = 0
		okbtn = wx.Button(self, wx.ID_OK)

		self.Bind(wx.EVT_CLOSE, self.OnExit)
		okbtn.Bind(wx.EVT_BUTTON, self.OnExit)
		self.text = wx.TextCtrl(self, style=wx.TE_MULTILINE)
		mainbox = wx.BoxSizer(wx.VERTICAL)
		mainbox.Add(self.text, 1, wx.ALL|wx.EXPAND|wx.GROW, border=5)
		mainbox.Add(okbtn, 0, wx.ALL|wx.ALIGN_RIGHT, border=20)

		self.text.SetEditable(False)
		self.SetAutoLayout(True)
		self.SetSizer(mainbox)
		#self.Fit()
		#self.Show(True)

	def setText(self, text):
		self.text.SetValue(text)


	def OnExit(self, event):
		self.Hide()


class AboutBox(wx.Dialog):
	text= """
Author: %s
Updater GUI Revision: %s
Copyright: %s
License: %s

Icon By: Anthony Piraino (from the Litho Extras Vol. 1)
Unzip by C. Spieler http://www.info-zip.org/ 
Unrar by  Alexander L. Roshal http://www.rarlab.com/rar_add.htm 
""" % (__author__, __version__, __copyright__, __license__)
	def __init__(self, parent, icon):
		wx.Dialog.__init__(self, parent, -1, "About WoW Addon Updater", size=(400, -1) )
		box = wx.BoxSizer(wx.VERTICAL)
		box.Add((1,10))
		title = wx.StaticText(self, label="WoW Addon Updater")

		font = title.GetFont()
		font.SetPointSize( font.GetPointSize()+4 )
		font.SetWeight(wx.FONTWEIGHT_BOLD)
		title.SetFont(font)
		box.Add( title, 0, wx.ALIGN_CENTER )
		try:	
			if icon != None:
				print icon
				self.SetIcon(icon)
				bmap = wx.BitmapFromIcon(icon)
				print bmap
				box.Add(wx.StaticBitmap(self, bitmap=bmap), 0, wx.ALIGN_CENTER)
		finally:
			pass

		box.Add( wx.StaticText(self, size=(380,-1), label=self.text), 1,wx.ALIGN_CENTER )
		box.Add( wx.Button(self, wx.ID_OK, "Okay"), 0, wx.ALIGN_CENTER)
		box.Add((1,10))
		self.SetSizer(box)


def wxSure(parent, message, caption = 'Are you sure?'): 
	dlg = wx.MessageDialog(parent, message, caption, wx.YES_NO | wx.NO_DEFAULT | wx.ICON_HAND | wx.STAY_ON_TOP)
	ret = dlg.ShowModal()
	dlg.Destroy() 
	return ret

def wxInfo(parent, message, caption = 'Insert program title'): 
    dlg = wx.MessageDialog(parent, message, caption, wx.OK | wx.ICON_INFORMATION) 
    dlg.ShowModal() 
    dlg.Destroy() 

if __name__ == "__main__":
	app = UpdaterApp(0)
	app.MainLoop()

