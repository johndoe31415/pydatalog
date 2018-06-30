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

class BaseCommand(object):
	def __init__(self):
		pass

	@staticmethod
	def commandid():
		raise Exception(NotImplemented)

class BaseResponse(object):
	def __init__(self, data):
		self._data = data

	@staticmethod
	def readlength():
		raise Exception(NotImplemented)

	def lengthok(self):
		return self.readlength() == len(self._data)

	@staticmethod
	def _convert_sint(value, bits):
		half = 1 << (bits - 1)
		if value >= half:
			value = -((1 << bits) - value)
		return value

	def _decode_uint8(self, offset):
		return self._data[offset]

	def _decode_uint16(self, offset):
		return (self._data[offset + 0] << 8) | (self._data[offset + 1] << 0)

	def _decode_sint8(self, offset):
		return self._convert_sint(self._decode_uint8(offset), 8)

	def _decode_sint16(self, offset):
		return self._convert_sint(self._decode_uint16(offset), 16)

	def _decode_datetime(self, offset):
		time_tuple = (self._decode_uint16(offset), self._decode_uint8(offset + 2), self._decode_uint8(offset + 3), self._decode_uint8(offset + 4), self._decode_uint8(offset + 5), self._decode_uint8(offset + 6))
		if time_tuple == (65535, 255, 255, 255, 255, 255):
			return None
		else:
			return datetime.datetime(*time_tuple)

	def _decode_string(self, offset, length):
		data = self._data[offset : offset + length]
		data = data.rstrip(b"\x00")
		data = data.lstrip(b"\xff")
		return data.decode("utf-8")
