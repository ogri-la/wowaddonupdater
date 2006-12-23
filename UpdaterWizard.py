#!/usr/bin/pythonw
'''
The purpose of this class it to provide a generalized method for 
creating wizard dialogues which allow the user to input answers
to a set of questions
'''

__author__    = "Patrick Butler <pbutler@killertux.org>"
__version__   = "$Revision: 31 $"
__copyright__ = "Copyright 2005,2006 Patrick Butler"
__license__   = "GPL Version 2"

import wx
import wx.wizard as wiz
import os.path
from wowaddon import DownloadError
from wowaddon import ParseError

class UpdaterWizard:
	def __init__(self, args):
		'''
		args is a list of dict's, one for each page
		each dict() containing at a minimum the following keys:
		title -- The title of the page
		type -- one of four values: str, int, choices, func
		  str -- value returned to be a string
		  int -- value returned to be an int
		  choices -- a list of strings for the user to choose from
		  func -- a text box will be shown for user input and then the value given will be used in a funciton, the function should return a list of strings to indicate possible choices
		desc -- a longer description for the page that is displayed above the control
		choices -- this is the list of choices
		desc2 -- this is only for the func type and is the description shown on the second page
		
		'''
		
		self.curpage = 0
		self.controls = []
		self.pages = []
		self.wizard = wiz.Wizard(None, -1, "Updater Wizard")
		self.pagect = []
		self.ret = [None]*len(args)
		self.funcs = {}
		self.ansindx = []
		self.types = []
		i = 0
		for a in args:
			if a['type'] == 'int' or a['type'] == 'str' or a['type'] == 'file' or a['type'] == 'dir' :
				(page, c) = self.makePage(a['title'], a['desc'], a['type'] )
				self.pages.append(page)
				self.controls.append(c)
				self.types.append(a['type'])
			elif a['type'] == 'choices':
				(page, c) = self.makePage(a['title'], a['desc'], a['type'], a['choices'] )
				self.pages.append(page)
				self.controls.append(c)
				self.types.append(a['type'])
			elif a['type'] == 'func':
				(pagefunc, cfunc) = self.makePage(a['title'], a['desc'], a['type1'] )
				self.pages.append(pagefunc)
				self.controls.append(cfunc)
				self.types.append(a['type1'])
				i += 1;
				self.funcs[i] = a['func']
				(page, c) = self.makePage(a['title'], a['desc2'], 'choices', [])
				self.pages.append(page)
				self.controls.append(c)
				self.types.append('choices')

			self.ansindx.append(i)
			i += 1
		for i in range(len(self.pages)-1):
			wiz.WizardPageSimple_Chain( self.pages[i], self.pages[i+1])
		self.wizard.FitToPage(self.pages[0])
		wiz.EVT_WIZARD_PAGE_CHANGING( self.wizard, self.wizard.GetId(), self.handler )
	

	def handler(self, event ):
		'''
		private function takes care of switching in between pages
		'''
		if event.GetDirection():
			self.curpage += 1
		else:
			self.curpage -= 1

		curpage = self.curpage
		if self.funcs.has_key(curpage):
			control = self.controls[curpage]
			control.Clear();
			try:
				if self.types[curpage-1] != 'None':
					inval = self.controls[curpage-1].GetValue();
					choices = self.funcs[curpage](inval)
				else:		
					choices = self.funcs[curpage]()
			except DownloadError:
				wx.MessageDialog(self.wizard, "Download Error, this probably means that the website is currently not available", "Download Error", style=wx.ICON_ERROR).ShowModal()
				
					
				choices = []
			for c in choices:
				if( type(c) == tuple ):
					(id, str) = c
					control.Append(str, id)
				else:
					control.Append(c, c)

		return True


	def makeChain(first, second):
		'''
		Private function for creating series of pages
		'''
		first.SetNext(second)
		second.SetPrev(first)
	
	def makePage(self, title=None, desc=None, type=None, other=None):
		'''
		Internal function to handle page creation itself
		'''
		wizPg = wiz.WizardPageSimple(self.wizard)
		control = None
		sizer = wx.BoxSizer(wx.VERTICAL)
		#sizer = self.wizard.GetPageAreaSizer()
		wizPg.SetSizer(sizer)
		if type == 'int' or type == 'str':
			control = wx.TextCtrl(wizPg)
		elif type == 'choices':
			control = wx.Choice(wizPg, choices=other)
		elif type == 'file' or type == 'dir':
			control = wx.TextCtrl(wizPg)
			browsebtn = wx.Button(wizPg, -1, "Browse")
			def OnBrowse(evt):
				path = control.GetValue() 
				if type == 'file':
					file = os.path.basename( path )
					dir = os.path.dirname( path )
					d = wx.FileDialog(wizPg, "Choose a file", dir, file)
				elif type == 'dir':
					d = wx.DirDialog(wizPg, "Choose a directory", path)
				#d.SetPath(control.GetValue() )
				#print control.GetValue() 
				d.ShowModal()
				control.SetValue(d.GetPath() )
				d.Destroy()

			browsebtn.Bind(wx.EVT_BUTTON, OnBrowse)

		elif control != None:
			control.Reparent(wizPg)
		elif type == 'None':
			control = None

		if title != None:
			title = wx.StaticText(wizPg, -1, title)
			title.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))
			sizer.Add(title, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
			sizer.Add(wx.StaticLine(wizPg), 0, wx.EXPAND|wx.ALL, 5)
		if desc != None:
			desc = wx.StaticText(wizPg, -1, desc)
			sizer.Add(desc, 0, wx.ALIGN_LEFT|wx.ALL, 5)
		if control != None:
			sizer.Add((5,5))
			sizer.Add(control, 0, wx.ALIGN_LEFT|wx.ALL|wx.EXPAND, 5)
		if type == 'file' or type == 'dir':
			sizer.Add(browsebtn, 0, wx.ALIGN_LEFT|wx.ALL, 5)

		return (wizPg, control)

	def Run(self):
		'''
		Calling this will start the wizard (there is no turning back)
		'''
		return self.wizard.RunWizard(self.pages[0])

	def Done(self):
		'''
		Call this when you're done 
		'''
		self.wizard.Destroy()
		self = []
	
	def getAnswers(self):
		'''
		Returns a list, one for each dict you gave in the constructor
		Type			Return Type
		--------------------------------------------------------
		str			string
		int			integer
		choice			tuple of the index and string
		func			tuple of the index and tring
		'''
		ret = []
		for i in self.ansindx:
			if self.types[i] == 'str' or self.types[i] == 'file' or self.types[i] == 'dir' :
				ret.append(self.controls[i].GetValue() )
			elif self.types[i] == 'int':
				try:
					ret.append(int(self.controls[i].GetValue()) )
				except ValueError:
					ret.append(0)
			
			elif self.types[i] == 'choices':
				val = self.controls[i].GetSelection() 
				data = self.controls[i].GetClientData(val)
				ret.append(  data )
		return ret
			
if __name__  == "__main__":
	def testfunc(x):
		return [ x+'1', x+'2' , x+'3' ]

	app = wx.PySimpleApp()
	w = UpdaterWizard( [ 
	{ 'type' : 'int', 'title' : "Title", 'desc' : "Long Description" },
	{ 'type' : 'choices', 'title' : "Title 2", 'desc' : "Long Description for Choices", 'choices' : [ 'poop', 'pipe' ] },
	{ 'type' : 'func', 'title' : "Title", 'desc' : "Long Description", 'func' : testfunc, 'desc2' : 'none', 'type1' : 'str' },
	{ 'type' : 'file', 'title' : "Title", 'desc' : "Long Description" },
	])
	#wizard.ShowPage(page1, False)
	if w.Run(): 
		print w.getAnswers()
	else:
		print "User Cancelled"
	w.Done()
	#wizard.Destroy()
	app.MainLoop()
	
