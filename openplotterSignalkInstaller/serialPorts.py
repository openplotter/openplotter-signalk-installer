#!/usr/bin/env python3

# This file is part of Openplotter.
# Copyright (C) 2019 by Sailoog <https://github.com/openplotter/openplotter-signalk-installer>
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

import ujson
from openplotterSettings import platform

class SerialPorts:
	def __init__(self,conf):
		self.conf = conf
		self.platform2 = platform.Platform()
		self.connections = []
		# {'app':'xxx', 'id':'xxx', 'data':'NMEA0183/NMEA2000/SignalK', 'device': '/dev/xxx', "baudrate": nnnnnn, "enabled": True/False}

	def usedSerialPorts(self):
		if self.platform2.skPort:
			try:
				setting_file = self.platform2.skDir+'/settings.json'
				data = ''
				with open(setting_file) as data_file:
					data = ujson.load(data_file)
				if 'pipedProviders' in data:
					for i in data['pipedProviders']:
						if i['pipeElements'][0]['options']['type'] == 'NMEA0183' or i['pipeElements'][0]['options']['type'] == 'NMEA2000' or i['pipeElements'][0]['options']['type'] == 'SignalK':
							if i['pipeElements'][0]['options']['subOptions']['type']=='serial' or i['pipeElements'][0]['options']['subOptions']['type']=='ngt-1-canboatjs' or i['pipeElements'][0]['options']['subOptions']['type']=='ngt-1':
								ID = i['id']
								datatype = i['pipeElements'][0]['options']['type']
								device = i['pipeElements'][0]['options']['subOptions']['device']
								baudrate = i['pipeElements'][0]['options']['subOptions']['baudrate']
								enabled = i['enabled']
								self.connections.append({'app':'Signal K','id':ID, 'data':datatype, 'device': device, 'baudrate': baudrate, "enabled": enabled})
			except:pass
			return self.connections