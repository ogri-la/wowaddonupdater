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
from wxPython.wx import *
import wx.gizmos
import UpdaterWizard
import updater

EVT_RESULT_ID = wxNewId()

def EVT_RESULT(win, func):
	win.Connect(-1, -1, EVT_RESULT_ID, func)

class ResultEvent(wxPyEvent):
	"""Simple event to carry arbitrary result data"""
	def __init__(self, data):
		wxPyEvent.__init__(self)
		self.SetEventType(EVT_RESULT_ID)
		self.data = data

class UpdaterApp(wxApp, updater.Updater):
	def OnInit(self):
		updater.Updater.__init__(self)
		self.main = UpdaterFrame(self, NULL, -1, "WoW AddOn Updater")
		self.main.Show(true)
		return True

	def error(self, str):
		updater.Updater.error(self, str)
		wxPostEvent(self.main,ResultEvent([4, str]))

	def out2(self, str):
		updater.Updater.out2(self, str)
		wxPostEvent(self.main,ResultEvent([2, str]))

	def out(self, str, nolog = 0): 
		updater.Updater.out(self, str, nolog)
		wxPostEvent(self.main,ResultEvent([1, str]))

	def gauge(self, i, max):
		updater.Updater.gauge(self, i, max)
		wxPostEvent(self.main,ResultEvent([3, i*100/max]))


class UpdaterFrame(wxFrame):
	def __init__(self, app, parent, ID, title):
		wxFrame.__init__(self, parent, ID, title, size=(600,-1))
		panel = wxPanel(self, -1)
		self.app = app
		self.count = 0
		self.icon = None
		# XXX see about integrating this into our app or a resource file
		try:            # - don't sweat it if it doesn't load
			if platform.system() != "Darwin":
				self.icon = wxIcon("updater.ico", wxBITMAP_TYPE_ICO)
				self.SetIcon(self.icon)
		finally: 
			pass


		mainbox = wxBoxSizer(wxVERTICAL)
		btnbox = wxBoxSizer(wxHORIZONTAL)
		textbox = wxBoxSizer(wxHORIZONTAL)


		#menubar stuff
		menubar = wxMenuBar()
		filemenu = wxMenu()
		helpmenu = wxMenu()

		logitm = filemenu.Append(-1,'L&og','Review the Log')
		exititm = filemenu.Append(-1,'E&xit','Terminate the program') 
		aboutitm = helpmenu.Append(wxID_ABOUT, '&About', 'About this program')
		helpitm = helpmenu.Append(-1,'Set the Preferences', '')

		self.Bind(wx.EVT_MENU, self.OnLog, logitm)
		self.Bind(wx.EVT_MENU, self.OnAbout, aboutitm)
		self.Bind(wx.EVT_MENU, self.OnExit, exititm)
		if "__WXMAC__" in wx.PlatformInfo:
			wxApp.SetMacExitMenuItemId(exititm.GetId())
		menubar.Append(filemenu,'&File')
 		menubar.Append(helpmenu,'&Help')
		self.SetMenuBar(menubar)

		#other stuff
		self.gauge = wxGauge(panel, -1, 100, size=(300, 25))
		self.startbtn = wxButton(panel, wxID_OK)
		self.prefbtn = wxButton(panel, -1, "Preferences") #wxID_STOP)
		self.text = wxStaticText(panel, -1, "Press OK to begin")

		self.Bind(EVT_BUTTON, self.OnOk, self.startbtn)
		self.Bind(EVT_BUTTON, self.OnPref, self.prefbtn)

		btnbox.Add(self.startbtn, 1, wxRIGHT, 10)
		btnbox.Add(self.prefbtn, 1)
		textbox.Add(self.text, 1)
		mainbox.Add((0, 50), 0)
		mainbox.Add(self.gauge, 0, wxALIGN_CENTRE)
		mainbox.Add((0, 30), 0)
		mainbox.Add(btnbox, 1, wxALIGN_CENTRE)
		mainbox.Add(textbox, 1, wxALIGN_CENTRE)

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
			wxMessageDialog(self, event.data[1], "Error", style=wxICON_ERROR).ShowModal()

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
	def __init__(self, app, parent, ID = -1, title = "Updater Preferences",  style=wxDEFAULT_FRAME_STYLE):
		wx.Dialog.__init__(self, parent, -1, title, size=(600, -1) )
		#wxFrame.__init__(self, parent, ID, title, size=(600,-1))
		panel = wxPanel(self, -1)
		
		#self.Show(True)
		#panel.Show(True)
		self.app = app
		self.count = 0
			
		self.Bind(EVT_CLOSE, self.OnExit)

		#first background controls like staticboxes
		mainbox = wxBoxSizer(wxVERTICAL)

		naddmodbox = wxStaticBoxSizer(
			wxStaticBox(panel, -1, "Add Mod"), wxVERTICAL)
		noptionbox = wxStaticBoxSizer(
			wxStaticBox(panel, -1, "General Options"), wxVERTICAL)
		ncurmodbox = wxStaticBoxSizer(
			wxStaticBox(panel, -1, "Current Mods"), wxVERTICAL)
		
		#create controls 
 		self.wowdirctrl = wxTextCtrl(panel)
 		self.wowdirbtn = wxButton(panel, -1, "Browse")
 		self.wowdirdia = wxDirDialog(panel, "WoW Directory")
 		#self.newmoddia = wxFileDialog(panel, "WoW Directory")

 		self.newmodtype = wxChoice(panel, choices=self.app.getModTypes())
 		#self.newmodbrs = wxButton(panel, -1, "Browse")
 		#self.newmodarg = wxTextCtrl(panel)
 		self.newmodbtn = wxButton(panel, -1, "Add Mod")

 		self.modlbox = wx.gizmos.EditableListBox(panel, style=wx.gizmos.EL_ALLOW_DELETE)
 		self.modsctrl = self.modlbox.GetListCtrl()
		self.delbtn = self.modlbox.GetDelButton()
		self.dnbtn  = self.modlbox.GetDownButton()
		self.upbtn  = self.modlbox.GetUpButton()
		
		self.helpbtn = wxButton(panel, -1, "Help")
		self.okbtn = wxButton(panel, -1, "OK")

		self.cleanbtn = wxButton(panel, -1, "Cleanup Files")


		#BIND buttons
		self.upbtn.Bind(EVT_BUTTON, self.OnUp)
		self.dnbtn.Bind(EVT_BUTTON, self.OnDown)
		self.delbtn.Bind(EVT_BUTTON, self.OnDel)
		self.helpbtn.Bind(EVT_BUTTON, self.OnHelp)
		self.okbtn.Bind(EVT_BUTTON, self.OnClose)
		self.cleanbtn.Bind(EVT_BUTTON, self.OnClean)
		self.wowdirbtn.Bind(EVT_BUTTON, self.OnBrowse)
		self.newmodbtn.Bind(EVT_BUTTON, self.OnAdd)
		#self.newmodbrs.Bind(EVT_BUTTON, self.OnBrowseArg)
		

		#option box
		optionbox = wxFlexGridSizer(cols=2, vgap=8, hgap=8)
		noptionbox.Add(optionbox, 1, wxGROW)
		noptionbox.Add(self.cleanbtn, 1, wxALIGN_CENTER|wxALL,5)

		optionbox.AddGrowableCol(1, 1)
		optionbox.SetFlexibleDirection(wxHORIZONTAL)
		wowdirbox = wxBoxSizer(wxHORIZONTAL)
		wowdirbox.Add(self.wowdirctrl, 1, wxRIGHT|wxGROW|wxEXPAND, 10)
		wowdirbox.Add(self.wowdirbtn, 0, wxALIGN_RIGHT)
		def addoption(label, ctrl):
			optionbox.Add( wxStaticText(panel, -1, label), 0)
			optionbox.Add( ctrl, 1, wxGROW )

		addoption("WoW Directory", wowdirbox)

		#add wow mod
		addmodbox = wxFlexGridSizer(cols=3, vgap=8, hgap=8)
		addmodbox.Add( wxStaticText(panel, -1, "Source:") )
		addmodbox.Add( self.newmodtype )
		addmodbox.Add( self.newmodbtn)
		#addmodbox.Add( self.newmodarg, 1, wxGROW|wxEXPAND)
		#addmodbox.Add( (0,0) )
		#addmodbox.Add( self.newmodbrs )
		#addmodbox.Add( (0,0) )
		naddmodbox.Add(addmodbox, 1, wxALIGN_CENTRE)

		ncurmodbox.Add(self.modlbox, 1, wxEXPAND)

		#all mod box
		modbox = wxBoxSizer(wxVERTICAL) #HORIZONTAL)
		modbox.Add( naddmodbox, 1, wxALL | wxEXPAND, border=5 )
		modbox.Add( (500,1) )
		modbox.Add( ncurmodbox, 3, wxALL | wxEXPAND, border=5 )

		#buttons box
		btnbox = wxBoxSizer(wxHORIZONTAL)
		btnbox.Add(self.helpbtn, 1, wxALIGN_RIGHT|wxRIGHT, 10)
		btnbox.Add(self.okbtn, 1, wxALIGN_RIGHT)
		#btnbox.Add((13,0) )
		
		#mainbox
		mainbox.Add(noptionbox, 0, wxALL|wxEXPAND, border=5)
		mainbox.Add(modbox, 1, wxALL | wxEXPAND, border=5)
		mainbox.Add(btnbox, 0, wxALIGN_RIGHT | wxBOTTOM | wxRIGHT, border=20)

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
			item = wxListItem()
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
			item = wxListItem()
			id = self.app.mods[0].id
			name = self.app.mods[0].getname()
			item.SetText("%s: %s, %s" %(type, id, name) )
			self.modsctrl.InsertItem(item)
		except ValueError:
			pass

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
		wxInfo(self, text, "Help")

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
		if choice == wxID_YES:
			self.app.fullclean()

class LogFrame(wxFrame):
	def __init__(self, app, parent, ID=-1, title="Log"):
		wxFrame.__init__(self, parent, ID, title, size=(400,600))
		self.app = app
		self.count = 0
		okbtn = wxButton(self, wxID_OK)

		self.Bind(EVT_CLOSE, self.OnExit)
		okbtn.Bind(EVT_BUTTON, self.OnExit)
		self.text = wxTextCtrl(self, style=wxTE_MULTILINE)
		mainbox = wxBoxSizer(wxVERTICAL)
		mainbox.Add(self.text, 1, wxALL|wxEXPAND|wxGROW, border=5)
		mainbox.Add(okbtn, 0, wxALL|wxALIGN_RIGHT, border=20)

		self.text.SetEditable(False)
		self.SetAutoLayout(True)
		self.SetSizer(mainbox)
		#self.Fit()
		#self.Show(True)

	def setText(self, text):
		self.text.SetValue(text)


	def OnExit(self, event):
		self.Hide()


class AboutBox(wxDialog):
	text= """
Author: %s
Updater GUI Revision: %s
Copyright: %s
License: %s

Icon By: Anthony Piraino (from the Litho Extras Vol. 1)
""" % (__author__, __version__, __copyright__, __license__)
	def __init__(self, parent, icon):
		wx.Dialog.__init__(self, parent, -1, "About WoW Addon Updater", size=(400, -1) )
		box = wxBoxSizer(wxVERTICAL)
		box.Add((1,10))
		title = wxStaticText(self, label="WoW Addon Updater")

		font = title.GetFont()
		font.SetPointSize( font.GetPointSize()+4 )
		font.SetWeight(wx.FONTWEIGHT_BOLD)
		title.SetFont(font)
		box.Add( title, 0, wxALIGN_CENTER )
		try:	
			if icon != None:
				print icon
				self.SetIcon(icon)
				bmap = wxBitmapFromIcon(icon)
				print bmap
				box.Add(wxStaticBitmap(self, bitmap=bmap), 0, wxALIGN_CENTER)
		finally:
			pass

		box.Add( wxStaticText(self, size=(380,-1), label=self.text), 1,wxALIGN_CENTER )
		box.Add( wx.Button(self, wx.ID_OK, "Okay"), 0, wxALIGN_CENTER)
		box.Add((1,10))
		self.SetSizer(box)


def wxSure(parent, message, caption = 'Are you sure?'): 
	dlg = wxMessageDialog(parent, message, caption, wxYES_NO | wxNO_DEFAULT | wxICON_HAND | wxSTAY_ON_TOP)
	ret = dlg.ShowModal()
	dlg.Destroy() 
	return ret

def wxInfo(parent, message, caption = 'Insert program title'): 
    dlg = wxMessageDialog(parent, message, caption, wxOK | wxICON_INFORMATION) 
    dlg.ShowModal() 
    dlg.Destroy() 

if __name__ == "__main__":
	app = UpdaterApp(0)
	app.MainLoop()

