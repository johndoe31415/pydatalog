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

import serial

class RC4Connection(object):
	_ADDRESS_ALL = 0xcc
	_ADDRESS_STATION_ID = 0x33

	def __init__(self, devpath, data_debug_callback = None):
		self._conn = serial.Serial("/dev/ttyUSB0", baudrate = 115200, timeout = 0.25)
		self._data_debug_callback = data_debug_callback

	def read(self, length, short_read_okay = False):
		read_data = bytearray()
		while len(read_data) < length:
			remaining_byte_count = length - len(read_data)
			next_chunk = self._conn.read(remaining_byte_count)
			if len(next_chunk) == 0:
				if not short_read_okay:
					raise Exception("Timeout when trying to read %d bytes from device. %d bytes received before timeout." % (length, len(read_data)))
				else:
					break
			read_data += next_chunk
		return bytes(read_data)

	@staticmethod
	def _enframe(data):
		assert(isinstance(data, bytes))
		cksum = sum(data) & 0xff
		return data + bytes([ cksum ])

	@staticmethod
	def _checkframe(data):
		assert(isinstance(data, bytes))
		cksum = sum(data[:-1]) & 0xff
		return data[-1] == cksum

	def _data_debug(self, identifier, data):
		if self._data_debug_callback is not None:
			self._data_debug_callback(identifier, data)

	def send(self, command, stationid = None, short_read_okay = False):
		rspclass = command.Response
		readlength = rspclass.readlength()

		txdata = command.serialize()
		if stationid is None:
			txdata = bytes([ self._ADDRESS_ALL, 0x00, command.commandid() ]) + txdata
		else:
			txdata = bytes([ self._ADDRESS_STATION_ID, stationid, command.commandid() ]) + txdata
		txdata = self._enframe(txdata)
		self._data_debug("-> TX", txdata)
		self._conn.write(txdata)

		rxdata = self.read(readlength, short_read_okay = short_read_okay)
		if len(rxdata) == 0:
			raise Exception("No response from device when trying to read %d bytes" % (readlength))
		if not self._checkframe(rxdata):
			raise Exception("Received checksum incorrect in %d byte frame: %s" % (len(rxdata), rxdata.hex()))

		response = rspclass(rxdata)
		if not response.lengthok():
			raise Exception("Short read, read %d bytes but received %d bytes." % (readlength, len(rxdata)))

		self._data_debug("<- RX", rxdata)
		return response

	def bytes2hex(data):
		return " ".join([ "%02x" % (c) for c in data ])
