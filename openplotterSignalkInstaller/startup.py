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
from openplotterSettings import language

class Start():
	def __init__(self, conf, currentLanguage):
		self.initialMessage = ''

		
	def start(self):
		green = ''
		black = ''
		red = ''

		return {'green': green,'black': black,'red': red}

class Check():
	def __init__(self, conf, currentLanguage):
		currentdir = os.path.dirname(os.path.abspath(__file__))
		language.Language(currentdir,'openplotter-signalk-installer',currentLanguage)
		self.initialMessage = _('Checking Signal K server...')


	def check(self):
		green = ''
		black = ''
		red = ''

		try:
			subprocess.check_output(['systemctl', 'is-active', 'signalk.service']).decode(sys.stdin.encoding)
			green = _('running')
		except:red = _('Signal K server is not running')

		return {'green': green,'black': black,'red': red}

