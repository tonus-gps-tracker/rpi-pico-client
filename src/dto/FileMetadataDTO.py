from libs.Dotenv import Dotenv
import json

env = Dotenv()

class FileMetadataDTO:

	last_readed = 0
	reserved = ''

	def __init__(self, last_readed = 0):
		self.last_readed = last_readed

	def __str__(self) -> str:
		return json.dumps(self.get())

	def get(self) -> dict:
		metadata = {
			'last_readed': self.last_readed,
			'reserved': ''
		}

		metadata['reserved'] = ' ' * (int(env.get('GPS_LOG_FILE_METADATA_LENGTH')) - len(json.dumps(metadata).encode('utf-8')))

		return metadata