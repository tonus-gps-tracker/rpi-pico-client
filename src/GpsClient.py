import utime
from machine import UART, Pin
from libs.MicropyGPS import MicropyGPS
from src.dto.LocationDTO import LocationDTO
from math import sin, cos, sqrt, atan2, radians

class GpsClient:

	_gps_data = MicropyGPS()
	_uart = UART(0)

	def __init__(self, rx_pin: int, tx_pin: int) -> None:
		self._uart.init(baudrate=9600, tx=Pin(tx_pin), rx=Pin(rx_pin))

	def get_location(self) -> LocationDTO | None:
		location = None

		try:
			while (self._uart.read()):
				pass

			while location == None:
				chars = self._uart.read(1024)

				if chars != None:
					chars = chars.decode('utf-8')

					for char in chars:
						self._gps_data.update(char)

					if self._gps_data.valid and self._gps_data.satellites_in_use:
						location = LocationDTO(
							self.parse_date_time(self._gps_data.date_string(formatting='s_dmy'), self._gps_data.timestamp),
							self.parse_latitude_longitude(self._gps_data.latitude),
							self.parse_latitude_longitude(self._gps_data.longitude),
							self._gps_data.altitude,
							self._gps_data.speed[2],
							self._gps_data.satellites_in_use
						)
		except Exception as error:
			print('[NEO6M] An exception occurred:', type(error).__name__, error)

		return location

	def parse_date_time(self, date: str, time: list) -> int:
		day, month, year = map(int, date.split('/'))
		hour, minute, second = map(int, time)

		return utime.mktime((year+2000, month, day, hour, minute, second, 0, 0))

	def parse_latitude_longitude(self, latlon: list) -> float:
		return (latlon[0] + (latlon[1] / 60)) * (-1 if latlon[2] in ('S', 'W') else 1)

	def distance(self, lat1, lon1, lat2, lon2) -> float:
		lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

		dlat = lat2 - lat1
		dlon = lon2 - lon1

		a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
		c = 2 * atan2(sqrt(a), sqrt(1 - a))

		return 6371.0 * 1000 * c