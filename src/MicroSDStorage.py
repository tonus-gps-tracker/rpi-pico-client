import uos
from machine import Pin, SPI
from libs.Dotenv import Dotenv
from libs.SDCard import SDCard

env = Dotenv()

class MicroSDStorage:

	def __init__(self):
		cs = Pin(int(env.get('MICROSD_CS_PIN')), Pin.OUT)

		spi = SPI(0,
			baudrate=9600,
			polarity=0,
			phase=0,
			bits=8,
			firstbit=SPI.MSB,
			sck=Pin(int(env.get('MICROSD_SCK_PIN'))),
			mosi=Pin(int(env.get('MICROSD_MOSI_PIN'))),
			miso=Pin(int(env.get('MICROSD_MISO_PIN')))
		)

		sd = SDCard(spi, cs)
		vfs = uos.VfsFat(sd)
		uos.mount(vfs, env.get('MICROSD_MOUNT_POINT'))
		uos.chdir(env.get('MICROSD_MOUNT_POINT'))

	def umount(self):
		uos.umount(env.get('MICROSD_MOUNT_POINT'))