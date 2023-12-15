import utime
from machine import UART, Pin
from libs.MicropyGPS import MicropyGPS
from src.dto.LocationDTO import LocationDTO

class GpsClient:

	_gpsData = MicropyGPS()
	_gpsModuleUART = UART(0)

	def __init__(self, rxPin: int, txPin: int):
		self._gpsModuleUART.init(baudrate=9600, tx=Pin(txPin), rx=Pin(rxPin))

	def get_location(self):
		location = None

		while (self._gpsModuleUART.read()):
			pass

		try:
			while location == None:
				chars = self._gpsModuleUART.read(1024)

				if chars != None:
					chars = chars.decode('utf-8')

					for char in chars:
						self._gpsData.update(char)

					if self._gpsData.valid and self._gpsData.satellites_in_use:
						location = LocationDTO(
							self.parse_date_time(self._gpsData.date_string(formatting='s_dmy'), self._gpsData.timestamp),
							self.parse_latitude_longitude(self._gpsData.latitude),
							self.parse_latitude_longitude(self._gpsData.longitude),
							self._gpsData.altitude,
							self._gpsData.speed[2],
							self._gpsData.satellites_in_use
						)
		except Exception as error:
				print('[GpsClient][get_location]: ' + str(error))

		return location

	def parse_date_time(self, date: str, time: list) -> int:
		day, month, year = map(int, date.split('/'))
		hour, minute, second = map(int, time)

		return utime.mktime((year+2000, month, day, hour, minute, second, 0, 0))

	def parse_latitude_longitude(self, latlon: list) -> float:
		return (latlon[0] + (latlon[1] / 60)) * (-1 if latlon[2] in ('S', 'W') else 1)
