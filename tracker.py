import _thread
import time
from GpsStorager import GpsStorager
from CloudUpdater import CloudUpdater
from libs.Dotenv import Dotenv
from src.MicroSDStorage import MicroSDStorage
from src.GpsLogManager import GpsLogManager

env = Dotenv()
storage = MicroSDStorage()
gpsLogManager = GpsLogManager()

shouldStop = False
isCloudUpdaterRunning = True

def cloudUpdaterThread(gpsLogManager: GpsLogManager):
	global shouldStop
	global isCloudUpdaterRunning

	cloudUpdater = CloudUpdater(gpsLogManager)

	while not shouldStop:
		cloudUpdater.run()
		time.sleep(int(env.get('GPRS_UPLOAD_INTERVAL')))

	isCloudUpdaterRunning = False

try:
	_thread.start_new_thread(cloudUpdaterThread, (gpsLogManager,))

	gpsStorager = GpsStorager(gpsLogManager)

	while not shouldStop:
		gpsStorager.run()
		time.sleep(int(env.get('GPS_LOG_INTERVAL')))
except KeyboardInterrupt:
	shouldStop = True

	while isCloudUpdaterRunning:
		time.sleep(1)

	gpsLogManager.close_current_file()
	storage.umount()