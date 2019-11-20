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

import subprocess, os
from openplotterSettings import conf
from openplotterSettings import language
from openplotterSettings import platform

def main():
	conf2 = conf.Conf()
	currentdir = os.path.dirname(__file__)
	currentLanguage = conf2.get('GENERAL', 'lang')
	language.Language(currentdir,'openplotter-signalk-installer',currentLanguage)
	platform2 = platform.Platform()

	try:
		print(_('Removing previous installations...'))

		if platform2.skDir:
			subprocess.call(['systemctl', 'stop', 'signalk.service'])
			subprocess.call(['systemctl', 'stop', 'signalk.socket'])
			subprocess.call(['rm', '-rf', platform2.skDir])
		skDir = conf2.home+'/.signalk'
		subprocess.call(['rm', '-rf', skDir])
		os.mkdir(skDir)

		print(_('Installing/Updating signal K server...'))

		subprocess.call(['npm', 'install', '--verbose', '-g', '--unsafe-perm', 'signalk-server'])

		print(_('Editing config files...'))

		fo = open(skDir+'/package.json', "w")
		fo.write( '{"name": "signalk-server-config","version": "0.0.1","description": "This file is here to track your plugin and webapp installs.","repository": {},"license": "Apache-2.0"}')
		fo.close()

		fo = open(skDir+'/settings.json', "w")
		fo.write( '{"interfaces": {},"ssl": false,"pipedProviders": [],"security": {"strategy": "./tokensecurity"}}')
		fo.close()

		fo = open(skDir+'/signalk-server', "w")
		fo.write( '#!/bin/sh\n/usr/lib/node_modules/signalk-server/bin/signalk-server -c '+skDir+' $*\n')
		fo.close()

		subprocess.call(['chown', '-R', conf2.user+':'+conf2.user, skDir])
		subprocess.call(['chmod', '775', skDir+'/signalk-server'])

		fo = open('/etc/systemd/system/signalk.socket', "w")
		fo.write( '[Socket]\nListenStream=3000\n\n[Install]\nWantedBy=sockets.target\n')
		fo.close()

		fo = open('/etc/systemd/system/signalk.service', "w")
		fo.write( '[Service]\nExecStart='+skDir+'/signalk-server\nRestart=always\nStandardOutput=syslog\nStandardError=syslog\nWorkingDirectory='+skDir+'\nUser='+conf2.user+'\nEnvironment=EXTERNALPORT=3000\n[Install]\nWantedBy=multi-user.target\n')
		fo.close()

		fo = open('/usr/share/applications/openplotter-signalk.desktop', "w")
		fo.write( '[Desktop Entry]\nName=Signal K\nExec=x-www-browser http://localhost:3000\nIcon=openplotter-signalk\nStartupNotify=true\nTerminal=false\nType=Application\nCategories=OpenPlotter')
		fo.close()

		subprocess.call(['systemctl', 'daemon-reload'])
		subprocess.call(['systemctl', 'enable', 'signalk.service'])
		subprocess.call(['systemctl', 'enable', 'signalk.socket'])
		subprocess.call(['systemctl', 'stop', 'signalk.service'])
		subprocess.call(['systemctl', 'restart', 'signalk.socket'])
		subprocess.call(['systemctl', 'restart', 'signalk.service'])
		
		print(' ')
		print(_('DONE'))

	except Exception as e: print(_('FAILED: ')+str(e))

if __name__ == '__main__':
	main()
