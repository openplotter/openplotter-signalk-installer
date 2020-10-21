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

class EditSettings:
	def __init__(self):
		self.platform = platform.Platform()
		self.setting_file = self.platform.skDir+'/settings.json'
		self.data = ''
		try:
			with open(self.setting_file) as data_file:
				self.data = ujson.load(data_file)
		except: self.data = ''

	def write(self):
		try:
			data2 = ujson.dumps(self.data, indent=4, sort_keys=True)
			file = open(self.setting_file, 'w')
			file.write(data2)
			file.close()
			return True
		except: return False

	def connectionIdExists(self, ID):
		for i in self.data['pipedProviders']:
			if i['id'] == ID: return True
		return False

	def setSerialConnection(self, ID, data, device, bauds):
		if data == 'NMEA 0183':
			self.data['pipedProviders'].append({'pipeElements': [{'type': 'providers/simple', 'options': {'logging': False, 'type': 'NMEA0183', 'subOptions': {"validateChecksum": True, "type": "serial", "device": device, "baudrate": int(bauds)}}}], 'enabled': True, 'id': ID})
		elif data == 'NMEA 2000':
			self.data['pipedProviders'].append({'pipeElements': [{'type': 'providers/simple', 'options': {'logging': False, 'type': 'NMEA2000', 'subOptions': {'device': device, "baudrate": int(bauds), 'type': 'ngt-1-canboatjs'}}}], 'enabled': True, 'id': ID})
		elif data == 'Signal K':
			self.data['pipedProviders'].append({'pipeElements': [{'type': 'providers/simple', 'options': {'logging': False, 'type': 'SignalK', 'subOptions': {"type": "serial", "device": device, "baudrate": int(bauds)}}}], 'enabled': True, 'id': ID})
		return self.write()

	def setNetworkConnection(self,ID,data,networkType,host,port):
		if data == 'NMEA0183':
			if networkType == 'UDP':
				self.data['pipedProviders'].append({'pipeElements': [{'type': 'providers/simple', 'options': {'logging': False, 'type': data, 'subOptions': {"validateChecksum": True, "type": "udp", "port": port}}}], 'enabled': True, 'id': ID})
			elif networkType == 'TCP':
				self.data['pipedProviders'].append({'pipeElements': [{'type': 'providers/simple', 'options': {'logging': False, 'type': data, 'subOptions': {"validateChecksum": True, "type": "tcp", "host": host, "port": port}}}], 'enabled': True, 'id': ID})
			elif networkType == 'GPSD':
				self.data['pipedProviders'].append({'pipeElements': [{'type': 'providers/simple', 'options': {'logging': False, 'type': data, 'subOptions': {"validateChecksum": True, "type": "gpsd", "host": host, "port": port}}}], 'enabled': True, 'id': ID})
		elif data == 'SignalK':
			if networkType == 'UDP':
				self.data['pipedProviders'].append({'pipeElements': [{'type': 'providers/simple', 'options': {'logging': False, 'type': data, 'subOptions': {"type": "udp", "port": port}}}], 'enabled': True, 'id': ID})
			elif networkType == 'TCP':
				self.data['pipedProviders'].append({'pipeElements': [{'type': 'providers/simple', 'options': {'logging': False, 'type': data, 'subOptions': {"type": "tcp", "host": host, "port": port}}}], 'enabled': True, 'id': ID})
		return self.write()

	def setCanbusConnection(self, ID, interface):
		self.data['pipedProviders'].append({'pipeElements': [{'type': 'providers/simple', 'options': {'logging': False, 'type': 'NMEA2000', 'subOptions': {'interface': interface, 'type': 'canbus-canboatjs'}}}], 'enabled': True, 'id': ID})
		return self.write()

	def setSeatalkConnection(self, ID, gpio, gpioInvert):
		self.data['pipedProviders'].append({'pipeElements': [{'type': 'providers/simple', 'options': {'logging': False, 'type': 'Seatalk', 'subOptions': {'gpio': gpio, 'gpioInvert': gpioInvert}}}], 'enabled': True, 'id': ID})
		return self.write()

	def removeConnection(self, ID):
		new = []
		for i in self.data['pipedProviders']:
			if i['id'] != ID: new.append(i)
		self.data['pipedProviders'] = new
		return self.write()

