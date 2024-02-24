import uos
from libs.Dotenv import Dotenv
from src.GpsLogManager import GpsLogManager

env = Dotenv()

class CloudUpdater:

	def __init__(self, gps_log_manager: GpsLogManager):
		self._gps_log_manager = gps_log_manager

	def run(self):
		file, is_file_open = self.get_file()

		if file is None:
			return

		data, end_file = self.get_data(file, is_file_open)

		if data is '':
			return

		print(data)

		# Envia dados para nuvem e se sucesso atualiza metadados

		data_length = len(data.encode('utf-8'))
		self.update_metadata(file, is_file_open, data_length)

		if not is_file_open:
			file.close()

			# if end_file:
			# 	self.backup(data/file.name) # TODO: erro no file.name

	def get_file(self):
		oldest_file_name = self.get_oldest_file_name()
		is_file_open = self._gps_log_manager.is_file_open(oldest_file_name)

		if not is_file_open:
			if oldest_file_name is '':
				return None, False

			file = open('data/' + oldest_file_name, 'r+')
		else:
			file = self._gps_log_manager.get_current_file()

		return file, is_file_open

	def get_oldest_file_name(self) -> str:
		files = uos.listdir('data')
		files = [file for file in files if file.startswith('20')]
		files = sorted(files)

		if files:
			return files[0]

		return ''

	def get_data(self, file, is_file_open: bool):
		if (is_file_open):
			self._gps_log_manager.current_file_lock.acquire()

		metadados = self._gps_log_manager.read_metadata(file)
		file.seek(int(env.get('GPS_LOG_FILE_METADATA_LENGTH')) + 1 + metadados['last_readed'])

		data = str('')
		end_file = False

		lines_per_request = int(env.get('GPRS_LINES_PER_REQUEST'))
		for _ in range(lines_per_request):
			line = str(file.readline())

			if line == '':
				end_file = True
				break

			data += line

		if (is_file_open):
			self._gps_log_manager.current_file_lock.release()

		return data, end_file

	def update_metadata(self, file, is_file_open: bool, data_length: int):
		if (is_file_open):
			self._gps_log_manager.current_file_lock.acquire()

		self._gps_log_manager.update_metadata(file, data_length)

		if (is_file_open):
			self._gps_log_manager.current_file_lock.release()

	def backup(self, file_path: str):
		uos.rename(file_path, 'backup/' + file_path.split('/')[1])