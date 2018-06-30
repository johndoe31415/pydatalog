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

import fractions
import enum
import datetime
from BaseCommand import BaseCommand, BaseResponse

def int16(value):
	value = value & 0xffff
	return bytes([ (value & 0xff00) >> 8, value & 0xff ])


class CommandGetDataInit(BaseCommand):
	@staticmethod
	def commandid():
		return 0x01

	def serialize(self):
		return b"\x00"

	class Response(BaseResponse):
		@staticmethod
		def readlength():
			return 11

		@property
		def startdatetime(self):
			return self._decode_datetime(0x3)


class CommandDownloadDataPage(BaseCommand):
	def __init__(self, pageno):
		self._pageno = pageno

	@staticmethod
	def commandid():
		return 0x02

	def serialize(self):
		return bytes([ self._pageno ])

	class Response(BaseResponse):
		@staticmethod
		def readlength():
			return 202

		def lengthok(self):
			return 2 <= len(self._data) <= 202

		@property
		def datapts(self):
			return (len(self._data) - 2) // 2

		@property
		def data(self):
			return [ fractions.Fraction(self._decode_sint16(offset), 10) for offset in range(1, len(self._data) - 1, 2) ]

class CommandSetParameters(BaseCommand):
	def __init__(self, **kwargs):
		self._loginterval_secs = kwargs.get("logintvl", 60)
		self._temp_upper = 600
		self._temp_lower = -300
		self._station = kwargs.get("stationid", 1)
		self._temp_calibration = 0

	@staticmethod
	def commandid():
		return 0x05

	def serialize(self):
		cmd = b"\x00"
		cmd += bytes([ self._loginterval_secs // 3600, self._loginterval_secs % 3600 // 60, self._loginterval_secs % 3600 % 60 ])
		cmd += int16(self._temp_upper)
		cmd += int16(self._temp_lower)
		cmd += bytes([ self._station ])

		cmd += b"\x31\x00"
		cmd += b"\x31\x00"
		cmd += bytes([ 0x31, self._temp_calibration ])
		cmd += b"\x00\x00\x00\x00\x00\x00"
		return cmd

	class Response(BaseResponse):
		@staticmethod
		def readlength():
			return 3

class DeviceStateEnum(enum.IntEnum):
	READY = 0
	LOGGING = 1
	STOPPED = 2
	WAITING = 3

class CommandGetParameters(BaseCommand):
	def serialize(self):
		return b"\x00"

	@staticmethod
	def commandid():
		return 0x06

	class Response(BaseResponse):
		@staticmethod
		def readlength():
			return 160

		def __init__(self, data):
			BaseResponse.__init__(self, data)

		@property
		def lastaccessdatetime(self):
			return self._decode_datetime(0xc)

		@property
		def startdatetime(self):
			return self._decode_datetime(0x14)

		@property
		def currentdatetime(self):
			return self._decode_datetime(0x1f)

		@property
		def userinfo(self):
			return self._decode_string(0x26, 100)

		@property
		def deviceid(self):
			return self._decode_string(0x8a, 10)

		@property
		def stationid(self):
			return self._data[1]

		@property
		def datapts(self):
			return self._decode_uint16(0x1d)

		@property
		def state(self):
			return DeviceStateEnum(self._data[0x13])

		@property
		def intervalsecs(self):
			return (self._data[5] * 3600) + (self._data[6] * 60) + self._data[7]

		@property
		def alarm_min(self):
			return fractions.Fraction(self._decode_sint16(0xa), 10)

		@property
		def alarm_max(self):
			return fractions.Fraction(self._decode_sint16(0x8), 10)

		@property
		def temp_cal(self):
			return fractions.Fraction(self._decode_sint8(0x98), 10)

		@property
		def delaytime(self):
			return fractions.Fraction(self._decode_sint8(0x94), 2)

		def dump(self):
			time_diff = (self.currentdatetime - datetime.datetime.utcnow()).total_seconds()
			elements = [ ]
			elements.append("State           : %s" % (self.state.name))
			elements.append("Station ID      : %d" % (self.stationid))
			elements.append("Current datetime: %s (%.0f seconds diff to UTC)" % (self.currentdatetime, time_diff))
			elements.append("Last access     : %s" % (self.lastaccessdatetime))
			elements.append("Start datetime  : %s" % (self.startdatetime))
			elements.append("User info       : %s" % (self.userinfo))
			elements.append("Device ID       : %s" % (self.deviceid))
			elements.append("Data points     : %d" % (self.datapts))
			elements.append("Interval time   : %d secs" % (self.intervalsecs))
			elements.append("Alarm min       : %.1f" % (self.alarm_min))
			elements.append("Alarm max       : %.1f" % (self.alarm_max))
			elements.append("Temperature cal : %.1f" % (self.temp_cal))
			elements.append("Delay time      : %.1f hrs" % (self.delaytime))
			elements = "\n".join(elements)
			print(elements)

class CommandSetDatetime(BaseCommand):
	def __init__(self, timestamp):
		self._timestamp = timestamp

	@staticmethod
	def commandid():
		return 0x07

	def serialize(self):
		cmd = b"\x00"
		cmd += int16(self._timestamp.year)
		cmd += bytes([ self._timestamp.month, self._timestamp.day, self._timestamp.hour, self._timestamp.minute, self._timestamp.second ])
		return cmd

	class Response(BaseResponse):
		@staticmethod
		def readlength():
			return 3


class CommandStopAcquisition(BaseCommand):
	@staticmethod
	def commandid():
		return 0x08

	def serialize(self):
		return b"\x00"

	class Response(BaseResponse):
		@staticmethod
		def readlength():
			return 3


class CommandSetUserInfo(BaseCommand):
	def __init__(self, newuserinfo):
		assert(isinstance(newuserinfo, str))
		self._userinfo = newuserinfo.encode("utf-8")
		if len(self._userinfo) > 100:
			raise Exception("User info may only have 100 chars at max")
		if len(self._userinfo) < 100:
			self._userinfo = self._userinfo + bytes([ 0 ] * (100 - len(self._userinfo)))
		assert(len(self._userinfo) == 100)

	@staticmethod
	def commandid():
		return 0x09

	def serialize(self):
		return b"\x00" + self._userinfo

	class Response(BaseResponse):
		@staticmethod
		def readlength():
			return 3


class CommandNop(BaseCommand):
	@staticmethod
	def commandid():
		return 0x0a

	def serialize(self):
		return b"\x00"

	class Response(BaseResponse):
		@staticmethod
		def readlength():
			return 3


class CommandSetID(BaseCommand):
	def __init__(self, newid):
		assert(isinstance(newid, str))
		self._id = newid.encode("utf-8")
		if len(self._id) > 10:
			raise Exception("ID may only have 10 chars at max")
		if len(self._id) < 10:
			self._id = self._id + bytes([ 0 ] * (10 - len(self._id)))
		assert(len(self._id) == 10)

	@staticmethod
	def commandid():
		return 0x0b

	def serialize(self):
		return b"\x00" + self._id

	class Response(BaseResponse):
		@staticmethod
		def readlength():
			return 3

