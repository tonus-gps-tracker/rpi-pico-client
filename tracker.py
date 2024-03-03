import _thread
import time
from GpsStorager import GpsStorager
from CloudUpdater import CloudUpdater
from libs.Dotenv import Dotenv
from src.MicroSDStorage import MicroSDStorage
from src.GpsLogManager import GpsLogManager

env = Dotenv()
storage = MicroSDStorage()
gps_log_manager = GpsLogManager()

should_stop = False
is_cloud_updater_running = False

def cloud_updater_thread():
	global is_cloud_updater_running

	try:
		is_cloud_updater_running = True

		cloud_updater = CloudUpdater(gps_log_manager)

		while not should_stop:
			cloud_updater.run()
			time.sleep(int(env.get('GPRS_UPLOAD_INTERVAL')))

		is_cloud_updater_running = False
	except:
		is_cloud_updater_running = False

try:
	_thread.start_new_thread(cloud_updater_thread, ())

	gps_storager = GpsStorager(gps_log_manager)

	while not should_stop:
		gps_storager.run()
		time.sleep(int(env.get('GPS_LOG_INTERVAL')))
except:
	should_stop = True

	while is_cloud_updater_running:
		time.sleep(1)

	gps_log_manager.close_current_file()
	storage.umount()