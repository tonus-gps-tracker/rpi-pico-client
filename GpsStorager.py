import time
from libs.Dotenv import Dotenv
from src.GpsClient import GpsClient
from src.FileManager import FileManager

env = Dotenv()

class GpsStorager:

	_lastTimestamp = 0
	_lastLatitude = 0.0
	_lastLongitude = 0.0

	def __init__(self, fileManager: FileManager):
		self._fileManager = fileManager
		self._gpsClient = GpsClient(int(env.get('GPS_RX_PIN')), int(env.get('GPS_TX_PIN')))

	def run(self):
		while True:
			location = self._gpsClient.get_location()

			if location != None:
				traveledDistance = self._gpsClient.distance(self._lastLatitude, self._lastLongitude, location.latitude, location.longitude)
				elapsedTimeSinceLastUpdate = location.timestamp - self._lastTimestamp

				if (traveledDistance > int(env.get('GPS_LOG_DISTANCE_THRESHOLD')) or elapsedTimeSinceLastUpdate > int(env.get('GPS_LOG_TIMEOUT'))):
					print(location)

					file = self._fileManager.get_file_by_timestamp(location.timestamp)
					self._fileManager.append(file, str(location) + '\n')

					self._lastTimestamp = location.timestamp
					self._lastLatitude = location.latitude
					self._lastLongitude = location.longitude

			time.sleep(int(env.get('GPS_LOG_INTERVAL')))