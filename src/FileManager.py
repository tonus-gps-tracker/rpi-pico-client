import uos
import time
import json
from src.dto.FileMetadataDTO import FileMetadataDTO
import src.common as common

class FileManager:

	_currentFile = None
	_currentFileName = None

	def read_metadata(self, file) -> dict:
		metadata = FileMetadataDTO().get()

		file.seek(0)
		data = file.readline()

		if data:
			metadata = json.loads(data)

		return metadata

	def is_file_open(self, fileName: str) -> bool:
		return self._currentFile != None and self._currentFileName == fileName

	def get_current_file(self):
		return self._currentFile

	def backup(self, filePath: str) -> None:
		uos.rename(filePath, 'backup/' + filePath.split('/')[1])

	def update_metadata(self, file, dataReadedLengh = 0):
		metadata = self.read_metadata(file)
		file.seek(0)
		file.write(str(FileMetadataDTO(metadata['last_readed'] + dataReadedLengh)) + '\n')

	def get_file_by_timestamp(self, timestamp: int):
		year, month, day, _, _, _, _, _ = time.localtime(timestamp)

		fileName = f'data/{year}-{common.lpad(str(month), 2, '0')}-{common.lpad(str(day), 2, '0')}.txt'

		if not self.file_exists(fileName):
			file = open(fileName, 'w+')
			self.update_metadata(file)
			file.close()

		if self._currentFile != None and self._currentFileName != fileName:
			self._currentFile.close()
			self._currentFile = None

		if self._currentFile == None:
			print('abriu o arquivo')
			file = open(fileName, 'r+')
			self._currentFile = file
			self._currentFileName = fileName

		return self._currentFile

	def append(self, file, data):
		file.seek(0, 2)
		file.write(data)

	def get_oldest_file_name(self):
		files = sorted(uos.listdir('data'))

		if files:
			return files[0]

		return None

	def file_exists(self, path: str) -> bool:
		try:
			uos.stat(path)
			return True
		except OSError:
			return False

	def close_current_file(self):
		if self._currentFile != None:
			self._currentFile.close()

	def __del__(self):
		self.close_current_file()