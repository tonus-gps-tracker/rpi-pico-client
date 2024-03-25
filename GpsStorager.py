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

			if location is None:
				return

			if (True or self.is_moving(location) or self.last_log_timed_out(location)):
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

		if location.n_satellites <= 3:
			distance_threshold = 20.0
		elif location.n_satellites <= 4:
			distance_threshold = 15.0
		elif location.n_satellites <= 5:
			distance_threshold = 10.0
		else:
			distance_threshold = 5.0

		return traveled_distance > distance_threshold

	def last_log_timed_out(self, location) -> bool:
		elapsed_time_since_last_update = location.timestamp - self._last_timestamp
		return elapsed_time_since_last_update > int(env.get('GPS_LOG_TIMEOUT'))