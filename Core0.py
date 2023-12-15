from libs.Dotenv import Dotenv
from src.GpsClient import GpsClient

env = Dotenv()

class Core0:

	def __init__(self):
		self._gpsClient = GpsClient(int(env.get('GPS_RX_PIN')), int(env.get('GPS_TX_PIN')))

	def run(self):
		while True:
			location = self._gpsClient.get_location()

			if location != None:
				pass
