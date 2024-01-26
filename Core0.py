import time
from libs.Dotenv import Dotenv
from src.GpsClient import GpsClient
from src.FileManager import FileManager

env = Dotenv()

class Core0:

	def __init__(self, fileManager: FileManager):
		self._fileManager = fileManager
		self._gpsClient = GpsClient(int(env.get('GPS_RX_PIN')), int(env.get('GPS_TX_PIN')))

	def run(self):
		while True:
			location = self._gpsClient.get_location()

			if location != None:
				file = self._fileManager.get_file_by_timestamp(location.timestamp)
				self._fileManager.append(file, str(location) + '\n')
				print(location)

			time.sleep(5)