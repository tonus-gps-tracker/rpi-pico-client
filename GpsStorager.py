import src.common as common
from libs.Dotenv import Dotenv
from src.GpsClient import GpsClient
from src.GpsLogManager import GpsLogManager

env = Dotenv()

class GpsStorager:

	_last_timestamp = 0
	_last_latitude = 0.0
	_last_longitude = 0.0

	def __init__(self, gps_log_manager: GpsLogManager):
		self._gps_log_manager = gps_log_manager
		self._gps_client = GpsClient(int(env.get('NEO6M_RX_PIN')), int(env.get('NEO6M_TX_PIN')))

	def run(self) -> None:
		location = self._gps_client.get_location()

		if location is None:
			return

		traveled_distance = self._gps_client.distance(self._last_latitude, self._last_longitude, location.latitude, location.longitude)
		elapsed_time_since_last_update = location.timestamp - self._last_timestamp

		if (traveled_distance > int(env.get('GPS_LOG_DISTANCE_THRESHOLD')) or elapsed_time_since_last_update > int(env.get('GPS_LOG_TIMEOUT'))):
			if common.debug():
				print(f'[NEO6M] {location}')

			with (self._gps_log_manager.file_manager_lock):
				self._gps_log_manager.write(location)

			self._last_timestamp = location.timestamp
			self._last_latitude = location.latitude
			self._last_longitude = location.longitude