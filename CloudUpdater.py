from libs.Dotenv import Dotenv
from src.FileManager import FileManager
import utime

env = Dotenv()

class CloudUpdater:

	def __init__(self, fileManager: FileManager):
		self._fileManager = fileManager

	def run(self):
		while True:
			file, isCurrentFile = self.get_file()

			if file is None:
				return

			metadados = self._fileManager.read_metadata(file)
			file.seek(51 + metadados['last_readed'])

			data = ''

			endFile = False

			linesPerRequest = 10
			for i in range(linesPerRequest):
				line = file.readline()

				if line == '':
					endFile = True
					break

				data += line

			# Envia dados para nuvem e se sucesso atualiza metadados

			dataLength = len(data.encode('utf-8'))
			self._fileManager.update_metadata(file, dataLength)

			if not isCurrentFile:
				file.close()

				if endFile:
					self._fileManager.backup(file.name)

			utime.sleep(10)

	def get_file(self):
		isCurrentFile = True

		oldestFileName = self._fileManager.get_oldest_file_name()
		isFileOpen = self._fileManager.is_file_open(oldestFileName)

		if not isFileOpen:
			if oldestFileName is '':
				return None, False

			file = open('data/' + oldestFileName, 'r+')
			isCurrentFile = False
		else:
			file = self._fileManager.get_current_file()

		return file, isCurrentFile
