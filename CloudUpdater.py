import uos
from libs.Dotenv import Dotenv
from src.GpsLogManager import GpsLogManager

env = Dotenv()

class CloudUpdater:

	def __init__(self, gpsLogManager: GpsLogManager):
		self._gpsLogManager = gpsLogManager

	def run(self):
		file, isFileOpen = self.get_file()

		if file is None:
			return

		data, endFile = self.get_data(file, isFileOpen)

		if data is '':
			return

		print(data)

		# Envia dados para nuvem e se sucesso atualiza metadados

		dataLength = len(data.encode('utf-8'))
		self.update_metadata(file, isFileOpen, dataLength)

		if not isFileOpen:
			file.close()

			# if endFile:
			# 	self.backup(data/file.name) # TODO: erro no file.name

	def get_file(self):
		oldestFileName = self.get_oldest_file_name()
		isFileOpen = self._gpsLogManager.is_file_open(oldestFileName)

		if not isFileOpen:
			if oldestFileName is '':
				return None, False

			file = open('data/' + oldestFileName, 'r+')
		else:
			file = self._gpsLogManager.get_current_file()

		return file, isFileOpen

	def get_oldest_file_name(self) -> str:
		files = uos.listdir('data')
		files = [file for file in files if file.startswith('20')]
		files = sorted(files)

		if files:
			return files[0]

		return ''

	def get_data(self, file, isFileOpen: bool):
		if (isFileOpen):
			self._gpsLogManager.current_file_lock.acquire()

		metadados = self._gpsLogManager.read_metadata(file)
		print('metadados', str(metadados)) # remover
		file.seek(int(env.get('GPS_LOG_FILE_METADATA_LENGTH')) + 1 + metadados['last_readed'])

		data = str('')

		endFile = False

		linesPerRequest = int(env.get('GPRS_LINES_PER_REQUEST'))
		for _ in range(linesPerRequest):
			line = str(file.readline())

			if line == '':
				endFile = True
				break

			data += line

		if (isFileOpen):
			self._gpsLogManager.current_file_lock.release()

		return data, endFile

	def update_metadata(self, file, isFileOpen: bool, dataLength: int):
		if (isFileOpen):
			self._gpsLogManager.current_file_lock.acquire()

		self._gpsLogManager.update_metadata(file, dataLength)

		if (isFileOpen):
			self._gpsLogManager.current_file_lock.release()

	def backup(self, filePath: str):
		uos.rename(filePath, 'backup/' + filePath.split('/')[1])