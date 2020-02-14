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

import subprocess, os, sys, ujson
from openplotterSettings import conf
from openplotterSettings import language
from openplotterSettings import platform

def main():
	conf2 = conf.Conf()
	currentdir = os.path.dirname(os.path.abspath(__file__))
	currentLanguage = conf2.get('GENERAL', 'lang')
	language.Language(currentdir,'openplotter-signalk-installer',currentLanguage)
	platform2 = platform.Platform()
	primaryPort = sys.argv[1]
	if primaryPort == '443':
		secundaryPort = '80'
		ssl = True
	elif primaryPort == '3443':
		secundaryPort = '3000' 
		ssl = True
	else: ssl = False

	print(_('Editing config files...'))
	
	try:
		subprocess.call(['systemctl', 'stop', 'signalk.service'])
		subprocess.call(['systemctl', 'stop', 'signalk.socket'])

		file = platform2.skDir+'/settings.json'
		with open(file) as data_file:
			data = ujson.load(data_file)
		data['ssl']= ssl
		data2 = ujson.dumps(data, indent=2, sort_keys=True)
		fo = open(file, "w")
		fo.write(data2)
		fo.close()

		fo = open('/etc/systemd/system/signalk.socket', "w")
		if ssl: fo.write( '[Socket]\nListenStream='+primaryPort+'\nListenStream='+secundaryPort+'\n\n[Install]\nWantedBy=sockets.target\n')
		else: fo.write( '[Socket]\nListenStream='+primaryPort+'\n\n[Install]\nWantedBy=sockets.target\n')
		fo.close()

		fo = open('/etc/systemd/system/signalk.service', "w")
		fo.write( '[Service]\nExecStart='+platform2.skDir+'/signalk-server\nRestart=always\nStandardOutput=syslog\nStandardError=syslog\nWorkingDirectory='+platform2.skDir+'\nUser='+conf2.user+'\nEnvironment=EXTERNALPORT='+primaryPort+'\n[Install]\nWantedBy=multi-user.target\n')
		fo.close()

		fo = open('/usr/share/applications/openplotter-signalk.desktop', "w")
		if ssl: http = 'https://'
		else: http = 'http://'
		fo.write( '[Desktop Entry]\nName=Signal K\nExec=x-www-browser '+http+'localhost:'+primaryPort+'\nIcon=openplotter-signalk\nStartupNotify=true\nTerminal=false\nType=Application\nCategories=OpenPlotter')
		fo.close()

		subprocess.call(['systemctl', 'daemon-reload'])
		subprocess.call(['systemctl', 'restart', 'signalk.socket'])
		subprocess.call(['systemctl', 'restart', 'signalk.service'])
		
		print(' ')
		print(_('DONE'))

	except Exception as e: print(_('FAILED: ')+str(e))

if __name__ == '__main__':
	main()
