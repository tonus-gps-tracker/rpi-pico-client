import _thread
import uos
import time
import json
import src.common as common
from src.dto.FileMetadataDTO import FileMetadataDTO
from src.dto.LocationDTO import LocationDTO

class GpsLogManager:

	_current_file = None
	_current_file_name = None

	file_manager_lock = _thread.allocate_lock()

	def _update_current_file_by_timestamp(self, timestamp: int):
		year, month, day, _, _, _, _, _ = time.localtime(timestamp)

		file_name = f'{year}-{common.lpad(str(month), 2, '0')}-{common.lpad(str(day), 2, '0')}.txt'
		file_path = f'data/{file_name}'

		if not self._file_exists(file_path):
			file = open(file_path, 'w+')
			self.update_metadata(file)
			file.close()

		if self._current_file != None and self._current_file_name != file_name:
			self._current_file.close()
			self._current_file = None

		if self._current_file == None:
			file = open(file_path, 'r+')
			self._current_file = file
			self._current_file_name = file_name

	def _file_exists(self, path: str) -> bool:
		try:
			uos.stat(path)
			return True
		except OSError:
			return False

	def is_file_open(self, file_name: str) -> bool:
		return file_name != '' and self._current_file != None and self._current_file_name == file_name

	def get_current_file(self):
		return self._current_file

	def close_current_file(self):
		if self._current_file != None:
			self._current_file.close()
			self._current_file = None
			self._current_file_name = None

	def read_metadata(self, file) -> dict:
		metadata = FileMetadataDTO().get()

		file.seek(0)
		data = file.readline()

		if data:
			metadata = json.loads(data)

		return metadata

	def update_metadata(self, file, data_readed_lengh = 0):
		metadata = self.read_metadata(file)
		file.seek(0)
		file.write(str(FileMetadataDTO(metadata['last_readed'] + data_readed_lengh)) + '\n')
		file.flush()

	def write(self, location: LocationDTO):
		self._update_current_file_by_timestamp(location.timestamp)

		if self._current_file != None:
			self._current_file.seek(0, 2)
			self._current_file.write(str(location) + '\n')
			self._current_file.flush()