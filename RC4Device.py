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

import time
import datetime
import calendar
import logging
import json

from Commands import CommandGetParameters, CommandDownloadDataPage, CommandStopAcquisition, CommandGetDataInit
from Commands import CommandNop, CommandSetID, CommandSetUserInfo, CommandSetDatetime, CommandSetParameters

class RC4Readout(object):
	def __init__(self, params, data):
		self._readoutdate = datetime.datetime.utcnow()
		self._params = params
		self._data = data

	def write_txt(self, f):
		print("# Readout of RC-4 device on %s UTC" % (self._readoutdate.strftime("%Y-%m-%d %H:%M:%S")), file = f)
		print("# Device ID          : %s" % (self._params.deviceid), file = f)
		print("# User Info          : %s" % (self._params.userinfo), file = f)
		print("# Data points        : %d" % (len(self._data)), file = f)
		print("# Interval time      : %d secs" % (self._params.intervalsecs), file = f)
		print("# Start of data      : %s" % (self._params.startdatetime.strftime("%Y-%m-%d %H:%M:%S")), file = f)
		print("# End of data        : %s" % (self._params.enddatetime.strftime("%Y-%m-%d %H:%M:%S")), file = f)
		print("# Current date       : %s" % (self._params.currentdatetime.strftime("%Y-%m-%d %H:%M:%S")), file = f)
		print("# Unit of acquisition: °C", file = f)
		print(file = f)
		delta = datetime.timedelta(0, self._params.intervalsecs)
		for (index, datapoint) in enumerate(self._data):
			timestamp = self._params.startdatetime + (index * delta)
			timet = calendar.timegm(timestamp.utctimetuple())
			print("%d	%s	%.1f" % (timet, timestamp.strftime("%Y-%m-%d %H:%M:%S"), datapoint), file = f)

	@staticmethod
	def _ts_json(ts):
		return {
			"timet":		calendar.timegm(ts.timetuple()),
			"iso":			ts.isoformat(timespec = "seconds"),
		}

	def write_json(self, f):
		json_data = {
			"readout_ts_utc":	self._ts_json(self._readoutdate),
			"device": {
				"id":			self._params.deviceid,
				"user_info":	self._params.userinfo,
			},
			"data": {
				"count":		len(self._data),
				"unit":			"C",
				"interval":		self._params.intervalsecs,
				"start":		self._ts_json(self._params.startdatetime),
				"end":			self._ts_json(self._params.enddatetime),
				"now":			self._ts_json(self._params.currentdatetime),
				"points":		[ float(value) for value in self._data ],
			},
		}
		print(json.dumps(json_data, sort_keys = True, indent = 4), file = f)

class RC4Device(object):
	_log = logging.getLogger("pydatalog.RC4Device")
	def __init__(self, conn):
		self._conn = conn

	def getstatus(self):
		params = self._conn.send(CommandGetParameters())
		time.sleep(0.2)
		return params

	def readout(self):
		params = self.getstatus()
		pages = (params.datapts + 99) // 100

		self._conn.send(CommandGetDataInit(), stationid = params.stationid)

		data = [ ]
		self._log.info("%d data points on device in %d pages", params.datapts, pages)
		for pageno in range(pages):
			self._log.debug("Reading page %d (%.0f%%)", pageno, pageno / pages * 100)
			rsp = self._conn.send(CommandDownloadDataPage(pageno), stationid = params.stationid, short_read_okay = (pageno == pages - 1))
			if len(rsp.data) == 0:
				break
			data += rsp.data
		self._log.debug("All pages read.")

		data = data[:params.datapts]
		return RC4Readout(params, data)

	def nop(self):
		self._conn.send(CommandNop())

	def stopacquisition(self):
		self._conn.send(CommandStopAcquisition())

	def synclocaltime(self):
		self._conn.send(CommandSetDatetime(datetime.datetime.now()))

	def syncutctime(self):
		self._conn.send(CommandSetDatetime(datetime.datetime.utcnow()))

	def setup(self, logintvl):
		cmd = CommandSetParameters(logintvl = logintvl)
		self._conn.send(cmd)

	def set_userinfo(self, info):
		self._conn.send(CommandSetUserInfo(info))

	def set_idinfo(self, info):
		self._conn.send(CommandSetID(info))
