import _thread
import uos
import time
import json
import src.common as common
from src.dto.FileMetadataDTO import FileMetadataDTO
from src.dto.LocationDTO import LocationDTO

class GpsLogManager:

	_currentFile = None
	_currentFileName = None

	current_file_lock = _thread.allocate_lock()

	def _update_current_file_by_timestamp(self, timestamp: int):
		year, month, day, _, _, _, _, _ = time.localtime(timestamp)

		fileName = f'{year}-{common.lpad(str(month), 2, '0')}-{common.lpad(str(day), 2, '0')}.txt'
		filePath = f'data/{fileName}'

		if not self._file_exists(filePath):
			file = open(filePath, 'w+')
			self.update_metadata(file)
			file.close()

		if self._currentFile != None and self._currentFileName != fileName:
			self._currentFile.close()
			self._currentFile = None

		if self._currentFile == None:
			file = open(filePath, 'r+')
			self._currentFile = file
			self._currentFileName = fileName

	def _file_exists(self, path: str) -> bool:
		try:
			uos.stat(path)
			return True
		except OSError:
			return False

	def is_file_open(self, fileName: str) -> bool:
		return fileName != '' and self._currentFile != None and self._currentFileName == fileName

	def get_current_file(self):
		return self._currentFile

	def close_current_file(self):
		if self._currentFile != None:
			self._currentFile.close()
			self._currentFile = None
			self._currentFileName = None

	def read_metadata(self, file) -> dict:
		metadata = FileMetadataDTO().get()

		file.seek(0)
		data = file.readline()

		if data:
			metadata = json.loads(data)

		return metadata

	def update_metadata(self, file, dataReadedLengh = 0):
		metadata = self.read_metadata(file)
		file.seek(0)
		file.write(str(FileMetadataDTO(metadata['last_readed'] + dataReadedLengh)) + '\n')
		file.flush()

	def write(self, location: LocationDTO):
		self._update_current_file_by_timestamp(location.timestamp)

		if self._currentFile != None:
			with (self.current_file_lock):
				self._currentFile.seek(0, 2)
				self._currentFile.write(str(location) + '\n')
				self._currentFile.flush()