import _thread
import uos
from GpsStorager import GpsStorager
from CloudUpdater import CloudUpdater
from libs.Dotenv import Dotenv
from MicroSDStorage import MicroSDStorage
from src.FileManager import FileManager

env = Dotenv()

MicroSDStorage()

fileManager = FileManager()

try:
	cloudUpdater = CloudUpdater(fileManager)
	_thread.start_new_thread(cloudUpdater.run, ())

	gpsStorager = GpsStorager(fileManager)
	gpsStorager.run()
except KeyboardInterrupt:
	fileManager.close_current_file()
	uos.umount(env.get('MICROSD_MOUNT_POINT'))
	print('exited successfully')

# TODO: Adicionar locker em manipulacao de arquivo (with)