#!/usr/bin/env python3

# This file is part of Openplotter.
# Copyright (C) 2015 by sailoog <https://github.com/sailoog/openplotter>
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
import subprocess, os, time
from openplotterSettings import conf
from openplotterSettings import language
from openplotterSettings import platform

def main():
	conf2 = conf.Conf()
	currentdir = os.path.dirname(__file__)
	currentLanguage = conf2.get('GENERAL', 'lang')
	language.Language(currentdir,'openplotter-signalk-installer',currentLanguage)
	
	subprocess.call(['npm', 'install', '-g', '--unsafe-perm', 'signalk-server'])

	subprocess.call(['x-terminal-emulator', '-e', 'signalk-server-setup'])

	platform2 = platform.Platform()
	if platform2.skPort:
		fo = open('/usr/share/applications/openplotter-signalk-installer.desktop', "w")
		fo.write( '[Desktop Entry]\nName=Signal K\nExec=x-www-browser '+platform2.http+'localhost:'+platform2.skPort+'\nIcon=openplotter-signalk-installer\nStartupNotify=true\nTerminal=false\nType=Application\nCategories=OpenPlotter')
		fo.close()
		print(' ')
		print(_('DONE!'))
	else:
		print(' ')
		print(_('FAILED! Try again please.'))

if __name__ == '__main__':
	main()
