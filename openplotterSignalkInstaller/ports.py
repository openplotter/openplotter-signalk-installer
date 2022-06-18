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

import os, ujson
from openplotterSettings import platform
from openplotterSettings import language

class Ports:
	def __init__(self,conf,currentLanguage):
		self.conf = conf
		currentdir = os.path.dirname(os.path.abspath(__file__))
		language.Language(currentdir,'openplotter-signalk-installer',currentLanguage)
		self.platform2 = platform.Platform()
		self.connections = []
		self.connections.append({'id':'skConn1', 'description':_('Signal K - Admin'), 'data':[], 'type':'TCP', 'mode':'server', 'address':'localhost', 'port':self.platform2.skPort, 'editable':'0'})
		self.connections.append({'id':'skConn2', 'description':_('Signal K - NMEA 0183 output'), 'data':[], 'type':'TCP', 'mode':'server', 'address':'localhost', 'port':'10110', 'editable':'0'})

	def usedPorts(self):
		if self.platform2.skPort:
			try:
				setting_file = self.platform2.skDir+'/settings.json'
				data = ''
				with open(setting_file) as data_file:
					data = ujson.load(data_file)
				if 'pipedProviders' in data:
					for i in data['pipedProviders']:
						if i['pipeElements'][0]['options']['subOptions']['type']=='udp':
							self.connections.append({'id':i['id'], 'description':_('Signal K connection'), 'data':[], 'type':'UDP', 'mode':'server', 'address':'localhost', 'port':i['pipeElements'][0]['options']['subOptions']['port'], 'editable':'0'})
						elif i['pipeElements'][0]['options']['subOptions']['type']=='tcp':
							if i['pipeElements'][0]['options']['subOptions']['host']=='localhost' or i['pipeElements'][0]['options']['subOptions']['host']=='127.0.0.1':
								self.connections.append({'id':i['id'], 'description':_('Signal K connection'), 'data':[], 'type':'TCP', 'mode':'client', 'address':'localhost', 'port':i['pipeElements'][0]['options']['subOptions']['port'], 'editable':'0'})
			except:pass
			return self.connections
