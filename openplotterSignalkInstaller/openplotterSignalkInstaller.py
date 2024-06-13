#!/usr/bin/env python3

# This file is part of OpenPlotter.
# Copyright (C) 2022 by Sailoog <https://github.com/openplotter/openplotter-signalk-installer>
#                  
# Openplotter is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# any later version.
# Openplotter is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Openplotter. If not, see <http://www.gnu.org/licenses/>.

import wx, os, webbrowser, subprocess, time
import wx.richtext as rt

from openplotterSettings import conf
from openplotterSettings import language
from openplotterSettings import platform
from .version import version

class MyFrame(wx.Frame):
	def __init__(self):
		self.conf = conf.Conf()
		self.platform = platform.Platform()
		self.currentdir = os.path.dirname(os.path.abspath(__file__))
		currentLanguage = self.conf.get('GENERAL', 'lang')
		self.language = language.Language(self.currentdir,'openplotter-signalk-installer',currentLanguage)

		wx.Frame.__init__(self, None, title=_('Signal K Installer')+' '+version, size=(800,444))
		self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
		icon = wx.Icon(self.currentdir+"/data/openplotter-signalk-installer.png", wx.BITMAP_TYPE_PNG)
		self.SetIcon(icon)
		self.CreateStatusBar()
		font_statusBar = self.GetStatusBar().GetFont()
		font_statusBar.SetWeight(wx.BOLD)
		self.GetStatusBar().SetFont(font_statusBar)

		self.toolbar1 = wx.ToolBar(self, style=wx.TB_TEXT)
		toolHelp = self.toolbar1.AddTool(101, _('Help'), wx.Bitmap(self.currentdir+"/data/help.png"))
		self.Bind(wx.EVT_TOOL, self.OnToolHelp, toolHelp)
		if not self.platform.isInstalled('openplotter-doc'): self.toolbar1.EnableTool(101,False)
		toolSettings = self.toolbar1.AddTool(102, _('Settings'), wx.Bitmap(self.currentdir+"/data/settings.png"))
		self.Bind(wx.EVT_TOOL, self.OnToolSettings, toolSettings)
		self.toolbar1.AddSeparator()
		toolReinstall = self.toolbar1.AddTool(104, _('Reinstall Signal K'), wx.Bitmap(self.currentdir+"/data/reinstall.png"))
		self.Bind(wx.EVT_TOOL, self.OnToolReinstall, toolReinstall)

		self.notebook = wx.Notebook(self)
		self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.onTabChange)
		self.settings = wx.Panel(self.notebook)
		self.output = wx.Panel(self.notebook)
		self.notebook.AddPage(self.settings, _('Settings'))
		self.notebook.AddPage(self.output, '')
		self.il = wx.ImageList(24, 24)
		img0 = self.il.Add(wx.Bitmap(self.currentdir+"/data/settings2.png", wx.BITMAP_TYPE_PNG))
		img1 = self.il.Add(wx.Bitmap(self.currentdir+"/data/output.png", wx.BITMAP_TYPE_PNG))
		self.notebook.AssignImageList(self.il)
		self.notebook.SetPageImage(0, img0)
		self.notebook.SetPageImage(1, img1)

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(self.toolbar1, 0, wx.EXPAND)
		vbox.Add(self.notebook, 1, wx.EXPAND)
		self.SetSizer(vbox)

		self.pageSettings()
		self.pageOutput()

		maxi = self.conf.get('GENERAL', 'maximize')
		if maxi == '1': self.Maximize()
		
		self.Centre() 

	def ShowStatusBar(self, w_msg, colour):
		self.GetStatusBar().SetForegroundColour(colour)
		self.SetStatusText(w_msg)

	def ShowStatusBarRED(self, w_msg):
		self.ShowStatusBar(w_msg, (130,0,0))

	def ShowStatusBarGREEN(self, w_msg):
		self.ShowStatusBar(w_msg, (0,130,0))

	def ShowStatusBarBLACK(self, w_msg):
		self.ShowStatusBar(w_msg, wx.BLACK) 

	def ShowStatusBarYELLOW(self, w_msg):
		self.ShowStatusBar(w_msg,(255,140,0))

	def onTabChange(self, event):
		try:
			self.SetStatusText('')
		except:pass

	def OnToolHelp(self, event): 
		url = "/usr/share/openplotter-doc/signalk/signalk_app.html"
		webbrowser.open(url, new=2)

	def OnToolSettings(self, event=0): 
		subprocess.call(['pkill', '-f', 'openplotter-settings'])
		subprocess.Popen('openplotter-settings')

	def OnToolShip(self, event): 
		url = self.platform.http+'localhost:'+self.platform.skPort+'/admin/#/serverConfiguration/settings'
		webbrowser.open(url, new=2)

	def OnToolReinstall(self, event): 
		msg = _('Installed plugins, login credentials and all current settings will be removed. Are you sure?')
		dlg = wx.MessageDialog(None, msg, _('Question'), wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
		if dlg.ShowModal() == wx.ID_YES:
			self.logger.Clear()
			self.notebook.ChangeSelection(1)
			self.ShowStatusBarYELLOW(_('Reinstalling Signal K, please wait... '))
			popen = subprocess.Popen(self.platform.admin+' signalkPostInstall reinstall', stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, shell=True)
			for line in popen.stdout:
				if not 'Warning' in line and not 'WARNING' in line:
					self.logger.WriteText(line)
					self.logger.ShowPosition(self.logger.GetLastPosition())
					wx.GetApp().Yield()
			self.restart_SK(0)
			self.refreshSettings()
		dlg.Destroy()

	def OnToolApply(self,e):
		msg = _('Only port and SSL settings will be changed. Installed plugins, login credentials and all current settings will be kept. Are you sure?')
		dlg = wx.MessageDialog(None, msg, _('Question'), wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
		if dlg.ShowModal() == wx.ID_YES:
			self.logger.Clear()
			self.notebook.ChangeSelection(1)
			self.ShowStatusBarYELLOW(_('Configuring Signal K port and SSL, please wait... '))
			popen = subprocess.Popen(self.platform.admin+' signalkSettings '+str(self.port.GetValue()), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, shell=True)
			for line in popen.stdout:
				if not 'Warning' in line and not 'WARNING' in line:
					self.logger.WriteText(line)
					self.logger.ShowPosition(self.logger.GetLastPosition())
					wx.GetApp().Yield()
			self.restart_SK(0)
			self.refreshSettings()
		dlg.Destroy()

	def OnToolCancel(self,e):
		self.refreshSettings()

	def pageSettings(self):
		portLabel = wx.StaticText(self.settings, label=_('Port'))
		self.port = wx.SpinCtrl(self.settings, 101, min=80, max=65536, initial=3000)
		self.port.Bind(wx.EVT_SPINCTRL, self.onPort)
		portText1 = wx.StaticText(self.settings, label=_('The Signal K default port is 3000'))
		portText2 = wx.StaticText(self.settings, label=_('Port 80 does not require ":3000" in browsers and app interfaces'))

		self.ssl = wx.CheckBox(self.settings, label=_('Enable SSL'))
		self.ssl.Bind(wx.EVT_CHECKBOX, self.onSsl)
		sslText1 = wx.StaticText(self.settings, label=_('The Signal K default SSL state is "disabled"'))
		sslText2 = wx.StaticText(self.settings, label=_('Enabling SSL for port 80 will result in port 443'))
		sslText3 = wx.StaticText(self.settings, label=_('Enabling SSL for any other port will result in port 3443'))

		self.toolbar2 = wx.ToolBar(self.settings, style=wx.TB_TEXT | wx.TB_VERTICAL)
		toolShip = self.toolbar2.AddTool(203, _('Vessel Data'), wx.Bitmap(self.currentdir+"/data/ship.png"))
		self.Bind(wx.EVT_TOOL, self.OnToolShip, toolShip)
		self.toolbar2.AddSeparator()
		toolApply = self.toolbar2.AddTool(205, _('Apply Changes'), wx.Bitmap(self.currentdir+"/data/apply.png"))
		self.Bind(wx.EVT_TOOL, self.OnToolApply, toolApply)
		toolCancel = self.toolbar2.AddTool(206, _('Cancel Changes'), wx.Bitmap(self.currentdir+"/data/cancel.png"))
		self.Bind(wx.EVT_TOOL, self.OnToolCancel, toolCancel)

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(portLabel, 0, wx.UP | wx.EXPAND, 5)
		hbox.Add(self.port, 0, wx.LEFT | wx.EXPAND, 10)

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.AddSpacer(20)
		vbox.Add(hbox, 0, wx.LEFT | wx.EXPAND, 20)
		vbox.AddSpacer(5)
		vbox.Add(portText1, 0, wx.LEFT | wx.EXPAND, 20)
		vbox.AddSpacer(5)
		vbox.Add(portText2, 0, wx.LEFT | wx.EXPAND, 20)
		vbox.AddSpacer(20)
		vbox.Add(self.ssl, 0, wx.LEFT | wx.EXPAND, 20)
		vbox.AddSpacer(5)
		vbox.Add(sslText1, 0, wx.LEFT | wx.EXPAND, 20)
		vbox.AddSpacer(5)
		vbox.Add(sslText2, 0, wx.LEFT | wx.EXPAND, 20)
		vbox.AddSpacer(5)
		vbox.Add(sslText3, 0, wx.LEFT | wx.EXPAND, 20)
		vbox.AddStretchSpacer(1)

		hbox0 = wx.BoxSizer(wx.HORIZONTAL)
		hbox0.Add(vbox, 1, wx.EXPAND, 0)
		hbox0.Add(self.toolbar2, 0, wx.EXPAND, 0)

		self.settings.SetSizer(hbox0)

		self.refreshSettings()

	def refreshSettings(self):
		self.platform = platform.Platform()
		self.notebook.ChangeSelection(0)
		if self.platform.skPort: self.port.SetValue(int(self.platform.skPort))
		if self.platform.http == 'https://': 
			self.ssl.SetValue(True)
			self.port.Disable()
		else: 
			self.ssl.SetValue(False)
			self.port.Enable()
		self.toolbar2.EnableTool(205,False)
		self.toolbar2.EnableTool(206,False)

	def restart_SK(self, msg):
		if msg == 0: msg = _('Restarting Signal K server... ')
		seconds = 12
		for i in range(seconds, 0, -1):
			self.ShowStatusBarYELLOW(msg+str(i))
			time.sleep(1)
		self.ShowStatusBarGREEN(_('Signal K server restarted'))

	def onPort(self, e):
		self.toolbar2.EnableTool(205,True)
		self.toolbar2.EnableTool(206,True)

	def onSsl(self, e=0):
		if self.ssl.GetValue():
			if self.port.GetValue() == 80: self.port.SetValue(443)
			else: self.port.SetValue(3443)
			self.port.Disable()
		else: 
			self.port.SetValue(3000)
			self.port.Enable()
		self.toolbar2.EnableTool(205,True)
		self.toolbar2.EnableTool(206,True)

	def pageOutput(self):
		self.logger = rt.RichTextCtrl(self.output, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_DONTWRAP|wx.LC_SORT_ASCENDING)
		self.logger.SetMargins((10,10))

		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.logger, 1, wx.EXPAND, 0)
		self.output.SetSizer(sizer)

def main():
	try:
		platform2 = platform.Platform()
		if not platform2.postInstall(version,'signalk'):
			subprocess.Popen(['openplotterPostInstall', platform2.admin+' signalkPostInstall'])
			return
	except: pass

	app = wx.App()
	MyFrame().Show()
	time.sleep(1)
	app.MainLoop()

if __name__ == '__main__':
	main()
