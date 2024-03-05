import time
import src.common as common
from machine import UART, Pin

class SIM800L:

	_uart = UART(1)

	def __init__(self, rx_pin: int, tx_pin: int):
		self._uart.init(baudrate=9600, tx=Pin(tx_pin), rx=Pin(rx_pin))

	def _clear_buffer(self) -> None:
		while (self._uart.read()):
			pass

	def _parse_bool_response(self, bool_response: bool) -> bool:
		if common.debug():
			print(f'[SIM800L][BoolResponse] {bool_response}')

		return bool_response

	def _read(self, timeout=1000) -> list:
		start_time = time.ticks_ms()
		response = b''

		while (time.ticks_ms() - start_time) < timeout:
			uart_response = self._uart.read()

			if uart_response != None:
				response += uart_response
				break

		return response.decode('utf-8').replace('\r', '').split('\n')

	def write(self, data: str) -> (int | None):
		return self._uart.write(data.encode('utf-8'))

	def AT(self, command: str) -> list:
		self._clear_buffer()

		if common.debug():
			print(f'[SIM800L][Command] {command}')

		self._uart.write((command + '\r\n').encode('utf-8'))

		response = self._read()
		if common.debug():
			print(f'[SIM800L][Response] {response}')

		return response

	def AT_plusCFUN(self, fun=1, rst=1) -> bool:
		response = self.AT(f'AT+CFUN={fun},{rst}')

		time.sleep(5)

		return self._parse_bool_response(len(response) == 3 and response[1] == 'OK')

	def AT_plusCSQ(self) -> int:
		signal_quality = 0

		response = self.AT('AT+CSQ')

		if self._parse_bool_response(len(response) == 5 and response[3] == 'OK'):
			try:
				signal_quality = int(response[1][6:response[1].index(',')])
			except ValueError:
				pass

		return signal_quality

	def AT_plusCOPS(self) -> str:
		provider = ''

		response = self.AT('AT+COPS?')

		if self._parse_bool_response(len(response) == 5 and response[3] == 'OK'):
			try:
				delimiter = '"'
				start = response[1].index(delimiter) + 1
				stop = response[1].index(delimiter, start)

				provider = response[1][start:stop]
			except ValueError:
				pass

		return provider

	def AT_plusSAPBR(self, cmd_type=3, cid=1, con_param_tag='Contype', con_param_value='GPRS') -> bool:
		if cmd_type == 3:
			response = self.AT(f'AT+SAPBR={cmd_type},{cid},\"{con_param_tag}\",\"{con_param_value}\"')
			return self._parse_bool_response(len(response) == 3 and response[1] == 'OK')
		elif cmd_type == 1:
			response = self.AT(f'AT+SAPBR={cmd_type},{cid}')
			return self._parse_bool_response(len(response) == 1 and response[0].startswith('AT+SAPBR'))

		return False

	def AT_plusCSTT(self, apn: str, user_name: str, password: str) -> bool:
		response = self.AT(f'AT+CSTT=\"{apn}\",\"{user_name}\",\"{password}\"')
		return self._parse_bool_response(len(response) == 3 and response[1] == 'OK')

	def AT_plusHTTPINIT(self) -> bool:
		response = self.AT('AT+HTTPINIT')
		return self._parse_bool_response(len(response) == 3 and response[1] == 'OK')

	def AT_plusHTTPPARA(self, tag: str, value: str) -> bool:
		response = self.AT(f'AT+HTTPPARA=\"{tag}\",\"{value}\"')
		return self._parse_bool_response(len(response) == 3 and response[1] == 'OK')

	def AT_plusHTTPDATA(self, size: int, time: int) -> bool:
		response = self.AT(f'AT+HTTPDATA={size},{time}')
		return self._parse_bool_response(len(response) == 3 and response[1] == 'DOWNLOAD')

	def AT_plusHTTPACTION(self, method=1) -> tuple[int, bool]:
		status = -1
		response = self.AT(f'AT+HTTPACTION={method}')

		if not self._parse_bool_response(len(response) == 3 and response[1] == 'OK'):
			return status, False

		response = self._read(10000)
		if common.debug():
			print(f'[SIM800L][Response] {response}')

		if self._parse_bool_response(len(response) == 3):
			try:
				delimiter = ','
				start = response[1].index(delimiter) + 1
				stop = response[1].index(delimiter, start)

				status = int(response[1][start:stop])
			except ValueError:
				return status, False

		return status, True

	def AT_plusHTTPTERM(self) -> bool:
		response = self.AT('AT+HTTPTERM')
		return self._parse_bool_response(len(response) == 3 and response[1] == 'OK')