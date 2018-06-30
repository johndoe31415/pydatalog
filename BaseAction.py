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

import logging
from RC4Connection import RC4Connection
from RC4Device import RC4Device
from HexDump import HexDump

class BaseAction(object):
	def __init__(self, cmd, args):
		self._cmd = cmd
		self._args = args

		lvl = {
			0:	logging.ERROR,
			1:	logging.INFO,
		}.get(self._args.verbose, logging.DEBUG)
		handler = logging.StreamHandler()
		handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))

		facility = logging.getLogger("pydatalog")
		facility.addHandler(handler)
		facility.setLevel(lvl)

		self._conn = RC4Connection(self._args.device, data_debug_callback = self._data_debug_callback)
		self._rc4dev = RC4Device(self._conn)
		self.run()



	def _data_debug_callback(self, identifier, data):
		if self._args.verbose >= 3:
			print("%s (%d bytes)" % (identifier, len(data)))
			HexDump().dump(data)
			print()

	def run(self):
		raise Exception(NotImplemented)
