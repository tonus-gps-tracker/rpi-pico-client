from libs.Dotenv import Dotenv
from src.FileManager import FileManager

env = Dotenv()

class Core1:

	def __init__(self, fileManager: FileManager):
		self._fileManager = fileManager

	def run(self):
		pass