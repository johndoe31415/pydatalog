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

import os
import sys
from BaseAction import BaseAction

class ActionDownload(BaseAction):
	def run(self):
		if os.path.exists(self._args.output) and not (self._args.force):
			self._log.error("Refusing to overwrite output file %s", self._args.output)
			sys.exit(1)

		data = self._rc4dev.readout()
		with open(self._args.output, "w") as f:
			if self._args.format == "txt":
				data.write_txt(f)
			elif self._args.format == "json":
				data.write_json(f)
			else:
				raise Exception(NotImplemented)
