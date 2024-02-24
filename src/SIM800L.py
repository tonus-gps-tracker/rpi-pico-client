import time
from machine import UART, Pin

class SIM800L:

	_uart = UART(1)

	def _init_(self, rx_pin: int, tx_pin: int) -> None:
		self._uart.init(baudrate=9600, tx=Pin(tx_pin), rx=Pin(rx_pin))

	def execute_AT(self, command: str, timeout=1000):
		self._clear_buffer()

		self._uart.write((command + '\r\n').encode('utf-8'))

		start_time = time.ticks_ms()
		response = b''

		while (time.ticks_ms() - start_time) < timeout:
			response += self._uart.read()

		return response

	def _clear_buffer(self):
		while (self._uart.read()):
			pass