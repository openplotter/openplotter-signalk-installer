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

import subprocess, os, sys
from openplotterSettings import conf
from openplotterSettings import language
from openplotterSettings import platform
from .version import version

def main():
	conf2 = conf.Conf()
	currentdir = os.path.dirname(os.path.abspath(__file__))
	currentLanguage = conf2.get('GENERAL', 'lang')
	language.Language(currentdir,'openplotter-signalk-installer',currentLanguage)
	platform2 = platform.Platform()
	if platform2.skDir: skDir = platform2.skDir
	else: skDir = conf2.home+'/.signalk'
	action = ''
	try:
		action = sys.argv[1]
	except:pass

	print(_('Checking sources...'))
	codeName = conf2.get('GENERAL', 'codeName')
	nodeVersion = '18'
	s = 'https://deb.nodesource.com/node_'+nodeVersion+'.x '+codeName
	deb = 'deb https://deb.nodesource.com/node_'+nodeVersion+'.x '+codeName+' main\ndeb-src https://deb.nodesource.com/node_'+nodeVersion+'.x '+codeName+' main'
	try:
		sources = subprocess.check_output('apt-cache policy', shell=True).decode(sys.stdin.encoding)
		if not s in sources:
			os.system('apt autoremove -y nodejs npm')
			fo = open('/etc/apt/sources.list.d/openplotterNodejs.list', "w")
			fo.write(deb)
			fo.close()
			os.system('cat '+currentdir+'/data/source/nodesource.gpg.key | gpg --dearmor > "/etc/apt/trusted.gpg.d/nodesource.gpg"')
			os.system('cp -f '+currentdir+'/data/source/99nodesource /etc/apt/preferences.d')
			os.system('apt update')
			os.system('apt install -y nodejs')
		print(_('DONE'))
	except Exception as e: print(_('FAILED: ')+str(e))

	print(_('Installing python packages...'))
	try:
		subprocess.call(['pip3', 'install', 'websocket-client', '-U', '--break-system-packages'])
		print(_('DONE'))
	except Exception as e: print(_('FAILED: ')+str(e))

	try:
		subprocess.call(['systemctl', 'stop', 'signalk.service'])
		subprocess.call(['systemctl', 'stop', 'signalk.socket'])

		print(_('Installing/Updating signal K server...'))
		
		os.system('npm install -g npm@latest')

		subprocess.call(['npm', 'install', '--verbose', '-g', 'signalk-server'])

		if action == 'reinstall':
			print(_('Removing previous installations...'))
			subprocess.call(['rm', '-rf', skDir])
			skDir = conf2.home+'/.signalk'
			subprocess.call(['rm', '-rf', skDir])
			conf2.set('GPIO', 'token', '')
			conf2.set('GPIO', 'href', '')
			conf2.set('I2C', 'token', '')
			conf2.set('I2C', 'href', '')
			conf2.set('IOB', 'token', '')
			conf2.set('IOB', 'href', '')
			conf2.set('MAIANA', 'token', '')
			conf2.set('MAIANA', 'href', '')
			conf2.set('NOTIFICATIONS', 'token', '')
			conf2.set('NOTIFICATIONS', 'href', '')
			conf2.set('PYPILOT', 'token', '')
			conf2.set('PYPILOT', 'href', '')
						
		if not os.path.exists(skDir+'/settings.json'):
			print(_('Editing config files...'))

			os.mkdir(skDir)

			fo = open(skDir+'/package.json', "w")
			fo.write( '{"name": "signalk-server-config","version": "0.0.1","description": "This file is here to track your plugin and webapp installs.","repository": {},"license": "Apache-2.0"}')
			fo.close()

			fo = open(skDir+'/settings.json', "w")
			fo.write( '{"interfaces": {},"ssl": false,"pipedProviders": [],"security": {"strategy": "./tokensecurity"}}')
			fo.close()

			node_path = subprocess.check_output(['npm', 'config', 'get', 'prefix']).decode(sys.stdin.encoding)
			node_path = node_path.replace('\n','')
			node_path = node_path.strip()
			fo = open(skDir+'/signalk-server', "w")
			fo.write( '#!/bin/sh\n'+node_path+'/lib/node_modules/signalk-server/bin/signalk-server -c '+skDir+' $*\n')
			fo.close()

			subprocess.call(['chown', '-R', conf2.user+':'+conf2.user, skDir])
			subprocess.call(['chmod', '775', skDir+'/signalk-server'])

			fo = open('/etc/systemd/system/signalk.socket', "w")
			fo.write( '[Socket]\nListenStream=3000\n\n[Install]\nWantedBy=sockets.target\n')
			fo.close()

			fo = open('/etc/systemd/system/signalk.service', "w")
			fo.write( '[Service]\nExecStart='+skDir+'/signalk-server\nRestart=always\nStandardOutput=journal\nStandardError=journal\nWorkingDirectory='+skDir+'\nUser='+conf2.user+'\nEnvironment=EXTERNALPORT=3000\n[Install]\nWantedBy=multi-user.target\n')
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
		
		print(_('DONE'))
	except Exception as e: print(_('FAILED: ')+str(e))

	print(_('Setting version...'))
	try:
		conf2.set('APPS', 'signalk', version)
		print(_('DONE'))
	except Exception as e: print(_('FAILED: ')+str(e))

if __name__ == '__main__':
	main()
