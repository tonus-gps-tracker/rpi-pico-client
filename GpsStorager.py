import src.common as common
from libs.Dotenv import Dotenv
from src.GpsClient import GpsClient
from src.GpsLogManager import GpsLogManager
from src.dto.LocationDTO import LocationDTO

env = Dotenv()

class GpsStorager:

	_last_timestamp = 0
	_last_latitude = 0.0
	_last_longitude = 0.0

	def __init__(self, gps_log_manager: GpsLogManager):
		self._gps_log_manager = gps_log_manager
		self._gps_client = GpsClient(int(env.get('NEO6M_RX_PIN')), int(env.get('NEO6M_TX_PIN')))

	def run(self) -> None:
		try:
			location = self._gps_client.get_location()

			if location is None or location.timestamp < self._gps_client.mktimeMinTimestamp:
				return

			if (self.is_moving(location) or self.last_log_timed_out(location)):
				if common.debug():
					print(f'[NEO6M] {location}')

				with (self._gps_log_manager.file_manager_lock):
					self._gps_log_manager.write(location)

				self._last_timestamp = location.timestamp
				self._last_latitude = location.latitude
				self._last_longitude = location.longitude
		except Exception as error:
			print('[GpsStorager] An exception occurred:', type(error).__name__, error)

	def is_moving(self, location: LocationDTO) -> bool:
		traveled_distance = self._gps_client.distance(self._last_latitude, self._last_longitude, location.latitude, location.longitude)

		distance_threshold = 16.0

		if location.n_satellites >= 10:
			distance_threshold = 12.0

		return traveled_distance > distance_threshold

	def last_log_timed_out(self, location) -> bool:
		elapsed_time_since_last_update = location.timestamp - self._last_timestamp
		return elapsed_time_since_last_update > int(env.get('GPS_LOG_TIMEOUT'))