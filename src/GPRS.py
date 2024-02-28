import time
from libs.Dotenv import Dotenv
from libs.SIM800L import SIM800L

env = Dotenv()

class GPRS:

	HTTP_STATUS_OK = 200

	def __init__(self, should_log=False) -> None:
		self.sim800l = SIM800L(int(env.get('SIM800L_RX_PIN')), int(env.get('SIM800L_TX_PIN')))
		self.sim800l.should_log(should_log)

	def is_service_available(self) -> bool:
		return self.sim800l.AT_plusCSQ() >= int(env.get('GPRS_MINIMUM_SIGNAL_QUALITY')) and self.sim800l.AT_plusCOPS() != ''

	def get_ip(self) -> str:
		ip = ''

		response = self.sim800l.AT('AT+SAPBR=2,1')

		if len(response) == 5 and response[3] == 'OK':
			try:
				delimiter = '"'
				start = response[1].index(delimiter) + 1
				stop = response[1].index(delimiter, start)

				ip = response[1][start:stop]
			except ValueError:
				pass

		return ip

	def setup(self) -> bool:
		sim_apn = env.get('SIM_APN')
		sim_user_name = env.get('SIM_USER_NAME')
		sim_password = env.get('SIM_PASSWORD')

		if not self.sim800l.AT_plusSAPBR() or \
			not self.sim800l.AT_plusCSTT(sim_apn, sim_user_name, sim_password) or \
			not self.sim800l.AT_plusSAPBR(1, 1):
				return False

		attempts = 0
		while self.get_ip() == '':
			attempts = attempts + 1

			if attempts > 60:
				return False

			time.sleep(1)

		return True

	def post_request(self, data: str) -> bool:
		api_endpoint = env.get('API_ENDPOINT')
		api_secret = env.get('API_SECRET')

		data_write_time = 80 * int(env.get('GPRS_LINES_PER_REQUEST'))

		if not self.sim800l.AT_plusHTTPINIT() or \
			not self.sim800l.AT_plusHTTPPARA('CID', '1') or \
			not self.sim800l.AT_plusHTTPPARA('URL', api_endpoint) or \
			not self.sim800l.AT_plusHTTPPARA('USERDATA', f'x-api-secret: {api_secret}') or \
			not self.sim800l.AT_plusHTTPPARA('CONTENT', 'application/text') or \
			not self.sim800l.AT_plusHTTPDATA(len(data), data_write_time):
				return False

		start_time = time.ticks_ms()
		self.sim800l.write(data)
		stop_time = time.ticks_ms()

		time.sleep_ms(data_write_time - (stop_time - start_time))

		status_code, success = self.sim800l.AT_plusHTTPACTION()

		if not success or \
			status_code != self.HTTP_STATUS_OK or \
			not self.sim800l.AT_plusHTTPTERM():
				return False

		return True