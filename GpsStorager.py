from libs.Dotenv import Dotenv
from src.GpsClient import GpsClient
from src.GpsLogManager import GpsLogManager

env = Dotenv()

class GpsStorager:

	_lastTimestamp = 0
	_lastLatitude = 0.0
	_lastLongitude = 0.0

	def __init__(self, gpsLogManager: GpsLogManager):
		self._gpsLogManager = gpsLogManager
		self._gpsClient = GpsClient(int(env.get('GPS_RX_PIN')), int(env.get('GPS_TX_PIN')))

	def run(self):
		location = self._gpsClient.get_location()

		if location is None:
			return

		traveledDistance = self._gpsClient.distance(self._lastLatitude, self._lastLongitude, location.latitude, location.longitude)
		elapsedTimeSinceLastUpdate = location.timestamp - self._lastTimestamp

		if (traveledDistance > int(env.get('GPS_LOG_DISTANCE_THRESHOLD')) or elapsedTimeSinceLastUpdate > int(env.get('GPS_LOG_TIMEOUT'))):
			self._gpsLogManager.write(location)

			self._lastTimestamp = location.timestamp
			self._lastLatitude = location.latitude
			self._lastLongitude = location.longitude