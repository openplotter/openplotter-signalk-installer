#!/usr/bin/env python3

# This file is part of OpenPlotter.
# Copyright (C) 2024 by Sailoog <https://github.com/openplotter/openplotter-signalk-installer>
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

import ujson, os, uuid

def main():
	security_file = 'security.json'

	if not os.path.exists(security_file):
		fo = open('security.json', "w")
		fo.write( '{"allow_readonly": true,"expiration": "NEVER","secretKey": "","users": [],"devices": [],"immutableConfig": false,"acls": [],"allowDeviceAccessRequests": true,"allowNewUserRegistration": true}')
		fo.close()

	save = False
	with open(security_file) as data_file:
		data = ujson.load(data_file)

	if 'secretKey' in data: secretKey = data['secretKey']
	else: secretKey = ''
	if not secretKey:
		for i in range(16):
			secretKey+= str(uuid.uuid4())
		secretKey = secretKey.replace('-','')
		data['secretKey'] = secretKey
		save = True

	if 'allow_readonly' in data: allow_readonly = data['allow_readonly']
	else: allow_readonly = False
	if not allow_readonly:
		data['allow_readonly'] = True
		save = True

	if not 'devices' in data: data['devices'] == []
	apps = ['GPIO','NOTIFICATIONS','I2C','MAIANA','PYPILOT','IOB']
	for i in apps:
		exists = False
		OPuuid = str(uuid.uuid4()).split('-')
		OPuuid[0] = i
		OPuuid = '-'.join(OPuuid)
		for index, value in enumerate(data['devices']):
			if value['description'] == 'OpenPlotter '+i:
				exists = True
				if not value['clientId']: 
					data['devices'][index]['clientId'] = OPuuid
					save = True
				if value['permissions'] != "readwrite": 
					data['devices'][index]['permissions'] = "readwrite"
					save = True
		if not exists: 
			data['devices'].append({"clientId": OPuuid,"permissions": "readwrite","description": "OpenPlotter "+i})
			save = True

	if save:
		data2 = ujson.dumps(data, indent=4)
		file = open(security_file, 'w')
		file.write(data2)
		file.close()

if __name__ == '__main__':
	main()