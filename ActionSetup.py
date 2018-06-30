#	pydatalog - Tool to read out temperature data loggers
#	Copyright (C) 2015-2018 Johannes Bauer
#
#	This file is part of pydatalog.
#
#	pydatalog is free software; you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation; this program is ONLY licensed under
#	version 3 of the License, later versions are explicitly excluded.
#
#	pydatalog is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#	Johannes Bauer <JohannesBauer@gmx.de>

import datetime

from BaseAction import BaseAction

class ActionSetup(BaseAction):
	def run(self):
		self._rc4dev.setup(self._args.interval)

		self._log.debug("Logging interval set to %d seconds" % (self._args.interval))

		now = datetime.datetime.now()
		delta = datetime.timedelta(0, self._args.interval * 16000)
		endtime = now + delta
		self._log.info("Acquisition duration: %s" % (str(delta)))
		self._log.info("End of acquisition: %s (local)" % (endtime.strftime("%Y-%m-%d %H:%M:%S")))
