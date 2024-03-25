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
is_gps_storager_running = False

def gps_storager_thread():
	global should_stop
	global is_gps_storager_running

	is_gps_storager_running = True

	gps_storager = GpsStorager(gps_log_manager)

	try:
		while not should_stop:
			gps_storager.run()
			time.sleep(int(env.get('GPS_LOG_INTERVAL')))
	except KeyboardInterrupt as error:
		print('[GpsStoragerThread] An exception occurred:', type(error).__name__, error)
		should_stop = True

	is_gps_storager_running = False

def cloud_updater_thread():
	global should_stop
	global is_cloud_updater_running

	is_cloud_updater_running = True

	cloud_updater = CloudUpdater(gps_log_manager)

	try:
		while not should_stop:
			cloud_updater.run()
			time.sleep(int(env.get('GPRS_UPLOAD_INTERVAL')))
	except KeyboardInterrupt as error:
		print('[CloudUpdaterThread] An exception occurred:', type(error).__name__, error)
		should_stop = True

	is_cloud_updater_running = False

def exit():
	while is_gps_storager_running or is_cloud_updater_running:
		time.sleep(1)

	gps_log_manager.close_current_day_file()
	storage.umount()

_thread.start_new_thread(cloud_updater_thread, ())
gps_storager_thread()

exit()