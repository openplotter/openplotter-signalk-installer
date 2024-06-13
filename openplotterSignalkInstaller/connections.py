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

import os, uuid, requests, ujson, ssl, time, jwt
from openplotterSettings import conf
from openplotterSettings import platform
from openplotterSettings import language
from websocket import create_connection

class Connections:
	def __init__(self, app):
		self.conf = conf.Conf()
		self.app = app
		self.platform = platform.Platform()
		self.currentdir = os.path.dirname(os.path.abspath(__file__))
		self.currentLanguage = self.conf.get('GENERAL', 'lang')
		self.language = language.Language(self.currentdir,'openplotter-signalk-installer',self.currentLanguage)
		if self.conf.get('GENERAL', 'debug') == 'yes': self.debug = True
		else: self.debug = False

		try:
			with open(self.platform.skDir+'/security.json') as data_file:
				self.data = ujson.load(data_file)
		except Exception as e:
			self.data = ''
			if self.debug: print('Error reading security.json: '+str(e))

		self.token = ''
		try:
			if 'secretKey' in self.data: 
				secretKey = self.data['secretKey']
				if secretKey:
					if 'devices' in self.data:
						for i in self.data['devices']:
							if i['description'] == 'OpenPlotter '+self.app:
								self.token = jwt.encode({ "device": i['clientId'] }, secretKey, algorithm="HS256")
		except Exception as e:
			self.token = ''
			if self.debug: print('Error getting token: '+str(e))

	def validate(self,rand):
		uri = self.platform.ws+'localhost:'+self.platform.skPort+'/signalk/v1/stream?subscribe=none'
		headers = {'Authorization': 'Bearer '+self.token}
		ws = create_connection(uri, header=headers, sslopt={"cert_reqs": ssl.CERT_NONE})
		sk = '{"updates":[{"$source":"OpenPlotter","values":[{"path":"validation.'+self.app+'","value":"'+rand+'"}]}]}\n'
		ws.send(sk)
		ws.close()
		r = requests.get(self.platform.http+'localhost:'+self.platform.skPort+'/signalk/v1/api/vessels/self', verify=False)
		contents = ujson.loads(r.content)
		return contents

	def checkConnection(self):
		#result = [error|validated]
		if not self.token:
			return ['error',_('Error connecting to Signal K. Reboot so that security credentials are created.')]
		else:
			rand = str(uuid.uuid4())
			try: contents = self.validate(rand)
			except:
				time.sleep(3)
				try: contents = self.validate(rand)
				except Exception as e:
					return ['error',_('Error validating Signal K connection: ')+str(e)+'.']
			if contents['validation'][self.app]['value'] == rand: return ['validated','']
			else: return ['error',_('Unexpected error validating connection.')]
