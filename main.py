import _thread
import uos
from Core0 import Core0
from Core1 import Core1
from libs.Dotenv import Dotenv
from src.Storage import Storage
from src.FileManager import FileManager

env = Dotenv()

Storage()

fileManager = FileManager()

try:
	# core1 = Core1(fileManager)
	# _thread.start_new_thread(core1.run, ())

	core0 = Core0(fileManager)
	core0.run()
except KeyboardInterrupt:
	fileManager.close_current_file()
	uos.umount(env.get('MICROSD_MOUNT_POINT'))
	print('exited successfully')