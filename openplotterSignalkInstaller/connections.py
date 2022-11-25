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

import os, uuid, requests, ujson, ssl, time
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

		self.uuid = self.conf.get(self.app, 'uuid')
		if not self.uuid:
			self.uuid = str(uuid.uuid4())
			self.conf.set(self.app, 'uuid', self.uuid)

		self.href = self.conf.get(self.app, 'href')

		self.token = self.conf.get(self.app, 'token')

		self.data = ''
		try:
			with open(self.platform.skDir+'/security.json') as data_file:
				self.data = ujson.load(data_file)
		except: self.data = ''

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
		#result = [pending|error|repeat|permissions|approved|validated,msg]
		if self.platform.skPort:
			if not self.token:
				if not self.href:
					try:
						r = requests.post(self.platform.http+'localhost:'+self.platform.skPort+'/signalk/v1/access/requests', data={"clientId":self.uuid, "description": "OpenPlotter "+self.app}, verify=False)
						contents = ujson.loads(r.content)
						if contents['statusCode'] == 202: 
							self.href = contents['href']
							self.conf.set(self.app, 'href', self.href)
							return ['pending',_('The access request must be aproved with read/write permission in Signal K administrator.')]
						else:
							self.conf.set(self.app, 'href', '')
							return ['repeat',_('Failed access request, status code: ')+contents['statusCode']+'.']
					except Exception as e:
						self.conf.set(self.app, 'href', '')
						return ['error',_('Error requesting access to Signal K server: ')+str(e)+'.']
				else:
					try:
						r = requests.get(self.platform.http+'localhost:'+self.platform.skPort+self.href, verify=False)
						contents = ujson.loads(r.content)
					except:
						self.conf.set(self.app, 'href', '')
						return ['repeat',_('The access request no longer exists.')]
					else: 
						if contents['statusCode'] == 202: return ['pending',_('The access request must be aproved with read/write permission in Signal K administrator.')]
						elif contents['statusCode'] == 200:
							if 'accessRequest' in contents:
								if 'permission' in contents['accessRequest']:
									if contents['accessRequest']['permission'] == 'DENIED':
										self.conf.set(self.app, 'href', '')
										return ['repeat',_('The access request was denied.')]
									elif contents['accessRequest']['permission'] == 'APPROVED':
										self.token = contents['accessRequest']['token']
										self.conf.set(self.app, 'href', '')
										self.conf.set(self.app, 'token', self.token)
										if self.data:
											if 'devices' in self.data:
												for i in self.data['devices']:
													if i['clientId'] == self.uuid:
														if i['permissions'] != 'readwrite':
															return ['permissions',_('Set read/write permission for this access in Signal K administrator.')]
										return ['approved',_('The access request was successfully approved.')]
			else:
				if self.data:
					if 'devices' in self.data:
						for i in self.data['devices']:
							if i['clientId'] == self.uuid:
								if i['permissions'] != 'readwrite':
									return ['permissions',_('Set read/write permission for this access in Signal K administrator.')]
				rand = str(uuid.uuid4())
				try: contents = self.validate(rand)
				except:
					time.sleep(3)
					try: contents = self.validate(rand)
					except Exception as e:
						return ['error',_('Unexpected error validating connection: ')+str(e)+'.']

				if contents['validation'][self.app]['value'] == rand: return ['validated','']
				else:
					self.conf.set(self.app, 'href', '')
					self.conf.set(self.app, 'token', '')
					return ['repeat',_('Failed validation.')]

		self.conf.set(self.app, 'href', '')
		self.conf.set(self.app, 'token', '')
		return ['error',_('Access to Signal K server could not be checked.')]
