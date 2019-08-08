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
import time, subprocess

#TODO set network startup
class Start():
	def __init__(self, conf):
		self.conf = conf
		self.initialMessage = ''
		try:
			subprocess.check_output(['systemctl', 'is-active', 'signalk.service']).decode('utf-8')
			self.initialMessage = _('Starting Signal K server...')
		except:pass

		
	def start(self):
		green = ''
		black = ''
		red = ''

		subprocess.call(['sudo', 'systemctl', 'start', 'signalk.socket'])
		subprocess.call(['sudo', 'systemctl', 'start', 'signalk.service'])
		time.sleep(2)
		black = _('started')
		return {'green': green,'black': black,'red': red}

class Check():
	def __init__(self, conf):
		self.conf = conf
		self.initialMessage = _('Checking Signal K server...')


	def check(self):
		green = ''
		black = ''
		red = ''

		try:
			subprocess.check_output(['systemctl', 'is-active', 'signalk.service']).decode('utf-8')
			green = _('running')
		except:red = _('Signal K server is not running')

		return {'green': green,'black': black,'red': red}

